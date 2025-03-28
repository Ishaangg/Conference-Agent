#!/usr/bin/env python3
"""
Pharmaceutical Industry Analyst Crew implementation using CrewAI 0.95.0.

This module provides a PharmaCrew class designed to be integrated with
the main conference attendee analysis flow. It analyzes attendees to determine
their association with the pharmaceutical industry and specific medical fields.
"""

import os
import json
import re
import csv
import time
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path
import concurrent.futures
from threading import Lock
import asyncio

from crewai import Agent, Crew, Process, Task
from conference.tools.web_search_tool import WebSearchTool
from conference.tools.async_web_search_tool import AsyncWebSearchTool
from conference.crews.pharma_crew.async_attendee_processor import AsyncAttendeeProcessor

def clean_json_text(text):
    """Clean the JSON text by removing markdown code blocks and other noise."""
    # Remove markdown code block markers
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```', '', text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # Replace any literals like "or" in the JSON with appropriate values
    text = re.sub(r'"Pharmaceutical"\s+or\s+"Healthcare"\s+or\s+"Other"', '"Pharmaceutical"', text)
    text = re.sub(r'"Pharma"\s+or\s+"Oncology"\s+or\s+"Women\'s Health"\s+or\s+"Organ Studies"\s+or\s+"Not a Lead"', '"Pharma"', text)
    
    return text

def export_to_csv(results: List[Dict[str, Any]], csv_file_path: str) -> None:
    """
    Export the analysis results to a CSV file.
    
    Args:
        results: List of analysis result dictionaries
        csv_file_path: Path to save the CSV file
    """
    try:
        if not results:
            print(f"⚠️ No results to export to CSV")
            return
            
        # Define the CSV fieldnames from the first result
        fieldnames = list(results[0].keys())
        
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
                
        print(f"📊 Results exported as CSV to: {csv_file_path}")
    except Exception as e:
        print(f"❌ Error exporting to CSV: {str(e)}")

def preprocess_attendees(attendees, batch_size, batch_index):
    """
    Prepare a batch of attendees for processing.
    
    Args:
        attendees: Full list of attendees
        batch_size: Size of each batch
        batch_index: Current batch index
        
    Returns:
        Current batch of attendees
    """
    total_attendees = len(attendees)
    batch_start = batch_index * batch_size
    batch_end = min(batch_start + batch_size, total_attendees)
    current_batch = attendees[batch_start:batch_end]
    
    print(f"\n🔄 PROCESSING BATCH {batch_index + 1} OF {(total_attendees + batch_size - 1)//batch_size}")
    print(f"Attendees {batch_start + 1}-{batch_end} out of {total_attendees}")
    
    return current_batch

class PharmaCrew:
    """
    Pharmaceutical Industry Analyst Crew
    
    A specialized crew that analyzes conference attendees to determine their association
    with the pharmaceutical industry and specific medical fields like oncology,
    women's health, and organ studies.
    
    This class is designed to be integrated with the main conference flow in main.py.
    """
    
    def __init__(self, attendees=None, output_file=None, batch_size=3, max_workers=3, 
                 max_concurrent_searches=5, use_async_processing=True, verbose=True):
        """
        Initialize the PharmaCrew.
        
        Args:
            attendees: List of attendee dictionaries
            output_file: Base filename for the CSV output (extension will be added automatically)
            batch_size: Number of attendees to analyze in each batch
            max_workers: Maximum number of concurrent workers for batch processing
            max_concurrent_searches: Maximum number of concurrent web searches per batch
            use_async_processing: Whether to use async processing for attendees within batches
            verbose: Whether to display detailed search results in logs
        """
        self.attendees = attendees
        self.output_file = output_file
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.max_concurrent_searches = max_concurrent_searches
        self.use_async_processing = use_async_processing
        self.verbose = verbose
        self.all_results = []
        self.batch_index = 0
        self.total_batches = 0
        self.results_lock = Lock()  # Add a lock for thread-safe results access
        
        # Load configuration
        self._load_configuration()
        
        # Initialize batch information if attendees are provided
        if self.attendees:
            self.total_batches = (len(self.attendees) + self.batch_size - 1) // self.batch_size
    
    def _load_configuration(self):
        """Load YAML configuration files for agents and tasks."""
        base_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        config_dir = base_dir / "config"
        
        # Load agents configuration
        agents_config_path = config_dir / "agents.yaml"
        with open(agents_config_path, 'r') as f:
            self.agents_config = yaml.safe_load(f)
            
        # Load tasks configuration
        tasks_config_path = config_dir / "tasks.yaml"
        with open(tasks_config_path, 'r') as f:
            self.tasks_config = yaml.safe_load(f)
            
        print("✅ Configuration loaded from YAML files")
    
    def create_pharma_analyst(self):
        """
        Create the pharmaceutical industry analyst agent based on configuration.
        
        Returns:
            Agent: The configured pharma analyst agent
        """
        # Create the agent using YAML configuration directly - without web search tool
        # since we already have search results from the async processor
        agent = Agent(
            config=self.agents_config["pharma_analyst"],
            tools=[],  # No tools needed as search results are already provided
            verbose=True
        )
        
        print(f"✅ Created agent: {agent.role}")
        return agent
    
    def create_analyze_task(self, agent, current_batch):
        """
        Create the attendee analysis task for a batch of attendees.
        
        Args:
            agent: The agent to assign to this task
            current_batch: The batch of attendees to analyze
            
        Returns:
            Task: The configured analysis task
        """
        # Prepare attendees data for the task context - direct JSON representation
        attendees_json = json.dumps(current_batch, indent=2)
        
        # Get the base task configuration
        task_config = self.tasks_config["analyze_attendees"].copy()
        
        # Replace placeholders in the task description with actual attendee data
        task_config["description"] = task_config["description"].format(
            attendee_count=len(current_batch),
            attendees_json=attendees_json
        )
        
        # Create task using the config
        task = Task(
            config=task_config,
            agent=agent
        )
        
        print(f"✅ Created task: Analyze {len(current_batch)} attendees")
        return task
    
    def create_crew(self, agents, tasks):
        """
        Create a crew with the specified agents and tasks.
        
        Args:
            agents: List of agents to include in the crew
            tasks: List of tasks for the crew to perform
            
        Returns:
            Crew: The configured crew
        """
        crew = Crew(
            agents=agents,
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            # Disable AgentOps telemetry to prevent errors
            disable_telemetry=True
        )
        
        print("✅ Created crew with sequential process (telemetry disabled)")
        return crew
    
    def process_batch(self, batch_index):
        """
        Process a single batch of attendees.
        
        Args:
            batch_index: Index of the batch to process
            
        Returns:
            The processed batch results
        """
        try:
            current_batch = preprocess_attendees(self.attendees, self.batch_size, batch_index)
            
            # Check if we should use async processing
            if self.use_async_processing:
                return self.process_batch_async(current_batch, batch_index)
            else:
                return self.process_batch_with_crew(current_batch, batch_index)
        except Exception as e:
            print(f"❌ Error processing batch {batch_index + 1}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
            
    def process_batch_async(self, current_batch, batch_index):
        """
        Process a batch of attendees using asynchronous processing.
        
        Args:
            current_batch: The batch of attendees to process
            batch_index: Index of the current batch
            
        Returns:
            List of processed attendee results
        """
        try:
            print(f"\n🚀 STARTING ASYNC PROCESSING FOR BATCH {batch_index + 1}")
            print("=" * 80)
            
            # Create an async attendee processor
            processor = AsyncAttendeeProcessor(
                max_concurrent_searches=self.max_concurrent_searches,
                rate_limit_delay=0.5,  # Add a small delay between requests to avoid rate limiting
                verbose=self.verbose
            )
            
            # Process the batch asynchronously using a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the attendee processing in the new loop to get search results
                search_results = loop.run_until_complete(processor.process_attendees(current_batch))
            finally:
                # Properly close the loop with all cleanup steps
                try:
                    # Cancel any pending tasks
                    pending = asyncio.all_tasks(loop)
                    if pending:
                        for task in pending:
                            task.cancel()
                        # Allow cancelled tasks to complete or process their cancellation
                        loop.run_until_complete(
                            asyncio.gather(*pending, return_exceptions=True)
                        )
                    
                    # Clear any remaining asyncgens
                    loop.run_until_complete(loop.shutdown_asyncgens())
                    
                    # Close the event loop
                    loop.close()
                except Exception as e:
                    print(f"Note: Error during event loop cleanup: {str(e)}")
            
            print(f"✅ Web search data gathered for {len(search_results)} attendees in batch {batch_index + 1}")
            
            # Now, pass the search results to the agent for classification
            # Create agent for this batch
            pharma_analyst = self.create_pharma_analyst()
            
            # Create a modified task that includes the search results
            # Prepare search results data for the task context
            search_results_json = json.dumps(search_results, indent=2)
            
            # Get the base task configuration
            task_config = self.tasks_config["analyze_attendees"].copy()
            
            # Replace placeholders in the task description with actual search results data
            task_config["description"] = task_config["description"].format(
                attendee_count=len(search_results),
                attendees_json=search_results_json
            )
            
            # Create task using the config
            analyze_task = Task(
                config=task_config,
                agent=pharma_analyst
            )
            
            # Create crew for this batch
            crew = self.create_crew(
                agents=[pharma_analyst],
                tasks=[analyze_task]
            )
            
            # Execute the crew
            print(f"\n🚀 STARTING CREW EXECUTION FOR BATCH {batch_index + 1} ANALYSIS")
            print("=" * 80)
            try:
                result = crew.kickoff()
            except Exception as e:
                # Check if it's the AgentOps error
                if "NoApiKeyException" in str(e) or "AgentOps" in str(e):
                    print(f"⚠️ AgentOps telemetry error caught in batch {batch_index + 1} - continuing without telemetry")
                    # Create a mock result with empty content
                    from collections import namedtuple
                    MockResult = namedtuple('MockResult', ['raw'])
                    result = MockResult(raw='[]')
                else:
                    # Re-raise if it's not the AgentOps error
                    raise
                    
            # Process the result
            cleaned_text = clean_json_text(result.raw)
            
            try:
                # Try to parse as JSON
                batch_results = json.loads(cleaned_text)
                print(f"✅ Batch {batch_index + 1} processed successfully: {len(batch_results)} attendees analyzed")
                return batch_results
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON for batch {batch_index + 1}: {str(e)}")
                # Try to clean and parse again with more aggressive cleaning
                try:
                    cleaned_text = re.sub(r'[^\[\]\{\}",:a-zA-Z0-9_\-\s]', '', cleaned_text)
                    batch_results = json.loads(cleaned_text)
                    print(f"✅ Recovered batch {batch_index + 1} with aggressive cleaning: {len(batch_results)} results")
                    return batch_results
                except:
                    print(f"❌ Could not recover batch {batch_index + 1} results - skipping this batch")
                    return []
            
        except Exception as e:
            print(f"❌ Error in async processing for batch {batch_index + 1}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def process_batch_with_crew(self, current_batch, batch_index):
        """
        Process a batch of attendees using the traditional crew approach.
        
        Args:
            current_batch: The batch of attendees to process
            batch_index: Index of the current batch
            
        Returns:
            List of processed attendee results
        """
        try:
            # Create agent for this batch
            pharma_analyst = self.create_pharma_analyst()
            
            # Create task for this batch
            analyze_task = self.create_analyze_task(pharma_analyst, current_batch)
            
            # Create crew for this batch
            crew = self.create_crew(
                agents=[pharma_analyst],
                tasks=[analyze_task]
            )
            
            # Execute the crew
            print(f"\n🚀 STARTING CREW EXECUTION FOR BATCH {batch_index + 1}")
            print("=" * 80)
            try:
                result = crew.kickoff()
            except Exception as e:
                # Check if it's the AgentOps error
                if "NoApiKeyException" in str(e) or "AgentOps" in str(e):
                    print(f"⚠️ AgentOps telemetry error caught in batch {batch_index + 1} - continuing without telemetry")
                    # Create a mock result with empty content
                    from collections import namedtuple
                    MockResult = namedtuple('MockResult', ['raw'])
                    result = MockResult(raw='[]')
                else:
                    # Re-raise if it's not the AgentOps error
                    raise
                    
            # Process the result
            cleaned_text = clean_json_text(result.raw)
            
            try:
                # Try to parse as JSON
                batch_results = json.loads(cleaned_text)
                print(f"✅ Batch {batch_index + 1} processed successfully with crew: {len(batch_results)} results")
                return batch_results
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON for batch {batch_index + 1}: {str(e)}")
                # Try to clean and parse again with more aggressive cleaning
                try:
                    cleaned_text = re.sub(r'[^\[\]\{\}",:a-zA-Z0-9_\-\s]', '', cleaned_text)
                    batch_results = json.loads(cleaned_text)
                    print(f"✅ Recovered batch {batch_index + 1} with aggressive cleaning: {len(batch_results)} results")
                    return batch_results
                except:
                    print(f"❌ Could not recover batch {batch_index + 1} results - skipping this batch")
                    return []
        except Exception as e:
            print(f"❌ Error in crew processing for batch {batch_index + 1}: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def save_final_results(self, skip_csv_export=False):
        """Save the combined results to CSV file if skip_csv_export is False."""
        if not self.all_results or not self.output_file or skip_csv_export:
            if skip_csv_export:
                print(f"📊 Analysis complete: {len(self.all_results)} total attendees analyzed (results not saved to file)")
            return
            
        # Export as CSV
        csv_output_file = os.path.splitext(self.output_file)[0] + ".csv"
        export_to_csv(self.all_results, csv_output_file)
        print(f"📊 Analysis complete: {len(self.all_results)} total attendees analyzed and saved to {csv_output_file}")
    
    def analyze(self, skip_csv_export=False):
        """
        Analyze all attendees in batches concurrently and return the results.
        
        This method processes attendees in batches concurrently using a thread pool,
        allowing multiple batches to be processed simultaneously.
        
        Args:
            skip_csv_export: If True, results won't be saved to CSV file

        Returns:
            List[Dict]: Analysis results as a list of dictionaries
        """
        try:
            if not self.attendees:
                print("No attendees to analyze")
                return []
            
            self.all_results = []
            total_attendees = len(self.attendees)
            self.total_batches = (total_attendees + self.batch_size - 1) // self.batch_size
            
            processing_mode = "ASYNC" if self.use_async_processing else "CREW-BASED"
            print(f"\n🔍 STARTING PHARMACEUTICAL INDUSTRY ANALYSIS ({processing_mode} MODE) 🔍")
            print(f"Total attendees: {total_attendees}")
            print(f"Batch size: {self.batch_size}")
            print(f"Total batches: {self.total_batches}")
            print(f"Max concurrent workers (batches): {self.max_workers}")
            print(f"Verbose logging: {'Enabled' if self.verbose else 'Disabled'}")
            
            if self.use_async_processing:
                print(f"Max concurrent web searches per batch: {self.max_concurrent_searches}")
            
            # Output file information
            if self.output_file and not skip_csv_export:
                csv_output_file = os.path.splitext(self.output_file)[0] + ".csv"
                print(f"Results will be saved to: {csv_output_file}")
            else:
                print(f"No output file specified or CSV export skipped - results will not be saved")
                
            print("=" * 80)
            
            # Process batches concurrently using ThreadPoolExecutor
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(self.max_workers, self.total_batches)) as executor:
                # Submit all batch processing tasks
                future_to_batch = {
                    executor.submit(self.process_batch, i): i 
                    for i in range(self.total_batches)
                }
                
                # Process completed batches as they finish
                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_index = future_to_batch[future]
                    try:
                        batch_results = future.result()
                        # Thread-safe update of all_results
                        with self.results_lock:
                            self.all_results.extend(batch_results)
                    except Exception as e:
                        print(f"❌ Exception processing batch {batch_index + 1}: {str(e)}")
            
            # Save final results
            self.save_final_results(skip_csv_export)
            
            return self.all_results
        except Exception as e:
            print(f"❌ Error in pharma crew analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return [] 