# Conference Attendee Analysis Workflow

## Overview

This diagram illustrates the asynchronous workflow implemented in the Conference Attendee Analysis system, specifically focusing on the concurrent processing of attendee batches in the PharmaCrew component.

## Main Workflow

1. **Start**: The process begins by loading CSV data with attendee information
2. **Clean & Validate**: The input file is cleaned and validated
3. **Process Attendees**: The data is processed into structured attendee objects
4. **Analyze Organizations**: Basic analysis counts attendees by organization
5. **Pharmaceutical Analysis**: Advanced analysis to identify pharmaceutical industry connections

## PharmaCrew Workflow (Concurrent Processing)

The PharmaCrew component implements concurrent batch processing:

1. **Initialize PharmaCrew**: Set up with attendees, batch size, and max workers
2. **Split Attendees**: Divide attendees into batches of configurable size
3. **Create Thread Pool**: Initialize the ThreadPoolExecutor with max_workers limit
4. **Concurrent Batch Processing**: Process multiple batches simultaneously:
   - Each batch gets its own agent, task, and crew
   - Batches execute in parallel up to the max_workers limit
5. **Thread-Safe Collection**: Results from all batches are collected using a lock mechanism
6. **Final Results**: All batch results are combined
7. **Save (Optional)**: Results can be saved to CSV or displayed directly

## Key Technical Components

- **ThreadPoolExecutor**: Enables parallel processing of attendee batches
- **Thread Lock**: Ensures thread-safe updating of the combined results
- **Configurable Parameters**:
  - Batch size: Controls how many attendees are in each batch
  - Max workers: Controls maximum concurrency level

To view the interactive diagram, open the HTML file in a web browser.
