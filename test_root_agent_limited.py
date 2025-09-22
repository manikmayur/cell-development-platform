#!/usr/bin/env python3
"""
Quick test for root agent with 1 iteration limit
"""

import asyncio
import sys
sys.path.insert(0, '.')

from adk_agent.agent import root_agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.agents.run_config import RunConfig
import uuid
from datetime import datetime

async def test_root_agent_quick(message: str, max_events: int = 20):
    """Test the root agent with a simple message."""
    
    print(f"🧪 Testing root agent (max_iterations=1) with: '{message}'")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Create session
    session_service = InMemorySessionService()
    session = session_service.create_session_sync(
        app_name="test",
        user_id="test_user",
        session_id="test_session",
        state={}
    )
    
    session.state['user_input'] = message
    session.state['context'] = {}
    
    # Create invocation context
    ctx = InvocationContext(
        invocation_id=str(uuid.uuid4()),
        agent=root_agent,
        session=session,
        session_service=session_service,
        run_config=RunConfig(max_llm_calls=8)  # Limit LLM calls to prevent loops
    )
    
    events = []
    event_count = 0
    content_events = 0
    
    try:
        async for event in root_agent._run_async_impl(ctx):
            event_count += 1
            events.append(event)
            
            # Extract content
            content = ""
            if hasattr(event, 'content') and event.content:
                content_obj = event.content
                if hasattr(content_obj, 'parts') and content_obj.parts:
                    for part in content_obj.parts:
                        if hasattr(part, 'text') and part.text:
                            content += part.text
                else:
                    content = str(content_obj)
            
            if content.strip():
                content_events += 1
                print(f"  📝 Event {event_count} (Content {content_events}): {content[:200]}{'...' if len(content) > 200 else ''}")
            else:
                print(f"  ⚡ Event {event_count}: {type(event).__name__}")
            
            # Break if too many events (safety)
            if event_count >= max_events:
                print(f"  ⚠️  Stopping after {max_events} events (safety limit)")
                break
                
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        print(f"  🔍 Traceback: {traceback.format_exc()[:500]}...")
        
    print(f"  ✅ Total events: {event_count}, Content events: {content_events}")
    print(f"  ⏰ Finished at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Show final session state
    final_state = dict(ctx.session.state)
    print(f"  📊 Session state keys: {list(final_state.keys())}")
    
    # Show important state values
    important_keys = ['task_execution_plan', 'quality_status', 'cell_design_output', 'user_input']
    for key in important_keys:
        if key in final_state:
            value = str(final_state[key])[:100]
            print(f"    {key}: {value}{'...' if len(str(final_state[key])) > 100 else ''}")
    
    return events, final_state

async def main():
    """Run quick tests."""
    
    test_cases = [
        ("hi", 15),
        ("hello, how are you?", 15),
        ("help me design a battery", 20)
    ]
    
    print("🚀 Testing Root Agent with max_iterations=1")
    print("=" * 60)
    
    for message, max_events in test_cases:
        print()
        events, final_state = await test_root_agent_quick(message, max_events)
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(main())