#!/usr/bin/env python3
"""
Event Summary Extractor for Root and Coordinating Agents
Captures and analyzes events from both agents to provide detailed summaries.
"""

import asyncio
import json
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add current directory to path for imports
sys.path.insert(0, '.')

# Import the agents
from adk_agent.agent import root_agent, task_coordinating_agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig


class EventSummaryExtractor:
    """Extracts and summarizes events from Google ADK agents."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.events = []
        
    async def extract_agent_events(self, agent, message: str, context: Dict[str, Any] = None, session_id: str = "test") -> Dict[str, Any]:
        """Extract events from a specific agent."""
        
        if context is None:
            context = {}
            
        try:
            # Create session
            session = self.session_service.create_session_sync(
                app_name="cell_development_platform",
                user_id="event_extractor",
                session_id=session_id,
                state=context
            )
            
            # Add message to session state
            session.state['user_input'] = message
            session.state['context'] = context
            
            # Create invocation context
            run_config = RunConfig()
            ctx = InvocationContext(
                invocation_id=str(uuid.uuid4()),
                agent=agent,
                session=session,
                session_service=self.session_service,
                run_config=run_config
            )
            
            # Collect events
            events = []
            event_count = 0
            
            print(f"\n🔍 Extracting events from {agent.name}...")
            
            async for event in agent._run_async_impl(ctx):
                event_count += 1
                event_data = self._extract_event_data(event, event_count)
                events.append(event_data)
                
                # Print real-time event info
                if event_data['content']:
                    print(f"  📝 Event {event_count}: {event_data['content'][:100]}...")
                elif event_data['type']:
                    print(f"  ⚡ Event {event_count}: {event_data['type']}")
                
            # Extract final session state
            final_state = dict(ctx.session.state)
            
            return {
                'agent_name': agent.name,
                'agent_description': getattr(agent, 'description', 'No description'),
                'message': message,
                'event_count': event_count,
                'events': events,
                'final_session_state': final_state,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
        except Exception as e:
            import traceback
            return {
                'agent_name': agent.name,
                'message': message,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def _extract_event_data(self, event, event_number: int) -> Dict[str, Any]:
        """Extract data from a single event."""
        event_data = {
            'event_number': event_number,
            'timestamp': datetime.now().isoformat(),
            'type': type(event).__name__,
            'content': '',
            'author': getattr(event, 'author', 'unknown'),
            'actions': {},
            'raw_attributes': {}
        }
        
        # Extract content
        if hasattr(event, 'content') and event.content:
            content = event.content
            if hasattr(content, 'parts') and content.parts:
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        event_data['content'] += part.text
            else:
                event_data['content'] = str(content)
        elif hasattr(event, 'message') and event.message:
            event_data['content'] = str(event.message)
        elif hasattr(event, 'text') and event.text:
            event_data['content'] = str(event.text)
        elif hasattr(event, 'data') and event.data:
            event_data['content'] = str(event.data)
        
        # Extract actions
        if hasattr(event, 'actions'):
            actions = event.actions
            if actions:
                event_data['actions'] = {
                    'escalate': getattr(actions, 'escalate', None),
                    'transfer': getattr(actions, 'transfer', None),
                    'tool_calls': getattr(actions, 'tool_calls', None),
                }
        
        # Store all attributes for debugging
        event_data['raw_attributes'] = {attr: str(getattr(event, attr, None)) 
                                       for attr in dir(event) 
                                       if not attr.startswith('_')}
        
        return event_data
    
    async def compare_agents(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Compare events from both root and coordinating agents."""
        
        print(f"\n🔬 Comparing agent events for message: '{message}'")
        
        # Extract events from both agents
        root_summary = await self.extract_agent_events(root_agent, message, context, "root_test")
        coord_summary = await self.extract_agent_events(task_coordinating_agent, message, context, "coord_test")
        
        # Create comparison summary
        comparison = {
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat(),
            'root_agent_summary': root_summary,
            'coordinating_agent_summary': coord_summary,
            'comparison': {
                'root_event_count': root_summary.get('event_count', 0),
                'coord_event_count': coord_summary.get('event_count', 0),
                'both_successful': root_summary.get('success', False) and coord_summary.get('success', False),
            }
        }
        
        return comparison
    
    def save_summary(self, summary: Dict[str, Any], filename: str = None):
        """Save event summary to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"event_summary_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"📁 Summary saved to: {filename}")
        return filename


async def main():
    """Main function to demonstrate event extraction."""
    extractor = EventSummaryExtractor()
    
    # Test messages
    test_messages = [
        "hi",
        "hello, how are you?",
        "help me design a battery cell",
        "what workflows are available?",
        "I need help with simulation"
    ]
    
    print("🚀 Starting Event Summary Extraction")
    print("="*50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n🧪 Test {i}/{len(test_messages)}: '{message}'")
        print("-" * 40)
        
        # Extract comparison
        comparison = await extractor.compare_agents(message)
        
        # Print summary
        print(f"\n📊 Summary for '{message}':")
        print(f"  🤖 Root Agent: {comparison['root_agent_summary'].get('event_count', 'ERROR')} events")
        print(f"  📋 Coord Agent: {comparison['coordinating_agent_summary'].get('event_count', 'ERROR')} events")
        print(f"  ✅ Success: {comparison['comparison']['both_successful']}")
        
        if not comparison['comparison']['both_successful']:
            print("  ❌ Error details:")
            if not comparison['root_agent_summary'].get('success'):
                print(f"    Root: {comparison['root_agent_summary'].get('error', 'Unknown error')}")
            if not comparison['coordinating_agent_summary'].get('success'):
                print(f"    Coord: {comparison['coordinating_agent_summary'].get('error', 'Unknown error')}")
        
        # Save detailed summary
        filename = f"event_summary_test_{i}_{message.replace(' ', '_').replace(',', '').replace('?', '')}.json"
        extractor.save_summary(comparison, filename)
    
    print(f"\n✅ Event extraction complete! Check the generated JSON files for detailed analysis.")


if __name__ == "__main__":
    asyncio.run(main())