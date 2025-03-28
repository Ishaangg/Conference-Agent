"""
Asynchronous Attendee Processor for PharmaCrew.

This module provides asynchronous processing capabilities for analyzing
attendees within a batch concurrently, improving performance by parallelizing
web search operations for each attendee.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
import time

from conference.tools.async_web_search_tool import AsyncWebSearchTool

class AsyncAttendeeProcessor:
    """
    Process attendees asynchronously using concurrent web searches.
    
    This class provides methods to gather web search data for multiple attendees in parallel
    within a batch, improving performance by running web searches concurrently.
    """
    
    def __init__(self, max_concurrent_searches=5, rate_limit_delay=1.0, verbose=True):
        """
        Initialize the async attendee processor.
        
        Args:
            max_concurrent_searches: Maximum number of concurrent web searches
            rate_limit_delay: Delay between searches to avoid rate limiting (in seconds)
            verbose: Whether to display detailed search results in logs
        """
        self.max_concurrent_searches = max_concurrent_searches
        self.rate_limit_delay = rate_limit_delay
        self.verbose = verbose
        self.search_tool = AsyncWebSearchTool()
        
    async def process_attendee(self, attendee: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single attendee asynchronously - gathering web search data only.
        
        Args:
            attendee: The attendee data dictionary
            
        Returns:
            Dictionary with attendee data and search results
        """
        try:
            # Extract attendee information
            first_name = attendee.get('first_name', '')
            last_name = attendee.get('last_name', '')
            organization = attendee.get('organization', '')
            email = attendee.get('email', '')
            
            # Create person name
            person_name = f"{first_name} {last_name}".strip()
            if not person_name:
                person_name = "Unknown"
            
            # Extract domain from email
            company_domain = email.split('@')[-1] if '@' in email else ''
            
            # Construct a more specific search query
            if organization:
                base_query = f"{person_name} {organization} "
            else:
                base_query = f"{person_name} "
                
            # Add targeted industry questions to make the query more specific
            search_query = (
                f"{base_query} pharmaceutical executive OR researcher OR scientist. "
                f"Is {person_name} associated with pharmaceutical industry, oncology, women's health, "
                f"or organ studies research? What therapeutic areas does {organization} focus on? "
                f"Role in clinical trials or drug development?"
            )
            
            # Perform web search
            print(f"\n🔎 Starting web search for: {person_name} ({organization})")
            search_result = await self.search_tool.execute_async({"query": search_query})
            
            # Log the search results if verbose
            if self.verbose:
                print(f"\n📄 SEARCH RESULTS FOR {person_name} ({organization}):")
                print("=" * 80)
                # Print a truncated version if too long
                if len(search_result) > 500:
                    print(f"{search_result[:500]}...\n[Content truncated, total length: {len(search_result)} chars]")
                else:
                    print(search_result)
                print("=" * 80)
            
            # Return attendee with search results for the agent to analyze
            result = {
                "person_name": person_name,
                "organization": organization or "Unknown",
                "email": email,
                "company_domain": company_domain or "unknown.com",
                "search_result": search_result
            }
            
            print(f"✅ Processed search for attendee: {person_name}")
            return result
            
        except Exception as e:
            print(f"❌ Error processing attendee {attendee.get('first_name', '')} {attendee.get('last_name', '')}: {str(e)}")
            # Return a minimal result with attendee data and error
            return {
                "person_name": f"{attendee.get('first_name', '')} {attendee.get('last_name', '')}".strip() or "Unknown",
                "organization": attendee.get('organization', '') or "Unknown",
                "email": attendee.get('email', ''),
                "company_domain": attendee.get('email', '').split('@')[-1] if '@' in attendee.get('email', '') else "unknown.com",
                "search_result": f"Error: {str(e)}"
            }
    
    async def process_attendees(self, attendees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple attendees concurrently.
        
        Args:
            attendees: List of attendee dictionaries
            
        Returns:
            List of processed attendee results with search data
        """
        if not attendees:
            return []
        
        print(f"\n🔄 STARTING ASYNC PROCESSING OF {len(attendees)} ATTENDEES")
        
        # Use semaphore to limit the number of concurrent web searches
        semaphore = asyncio.Semaphore(self.max_concurrent_searches)
        
        async def process_with_semaphore(attendee):
            async with semaphore:
                # Add a small delay to avoid hitting rate limits
                if self.rate_limit_delay > 0:
                    await asyncio.sleep(self.rate_limit_delay)
                return await self.process_attendee(attendee)
        
        try:
            # Process all attendees concurrently with controlled concurrency
            start_time = time.time()
            results = await asyncio.gather(*[process_with_semaphore(attendee) for attendee in attendees])
            end_time = time.time()
            
            print(f"✅ COMPLETED ASYNC PROCESSING OF {len(attendees)} ATTENDEES IN {end_time - start_time:.2f} SECONDS")
            
            return results
        except Exception as e:
            print(f"❌ Error in async processing: {str(e)}")
            raise 