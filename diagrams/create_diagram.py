import matplotlib.pyplot as plt
import numpy as np
import os

def create_workflow_diagram():
    """Create a workflow diagram of the Conference Agent system"""
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Remove axes
    ax.axis('off')
    
    # Define node positions
    positions = {
        # Main flow nodes
        "Start": (0.5, 0.95),
        "LoadCSV": (0.5, 0.9),
        "CleanFile": (0.5, 0.85),
        "ProcessData": (0.5, 0.8),
        "AnalyzeOrgs": (0.5, 0.75),
        "PharmaAnalysis": (0.5, 0.7),
        
        # PharmaCrew flow
        "InitPharmaCrew": (0.5, 0.62),
        "SplitBatches": (0.5, 0.55),
        "ThreadPool": (0.5, 0.48),
        
        # Concurrent processing nodes
        "Batch1": (0.25, 0.4),
        "Batch2": (0.42, 0.4),
        "Batch3": (0.58, 0.4),
        "BatchN": (0.75, 0.4),
        
        # Batch detail nodes
        "CreateAgent": (0.93, 0.5),
        "CreateTask": (0.93, 0.45),
        "CreateCrew": (0.93, 0.4),
        "RunCrew": (0.93, 0.35),
        "ProcessResults": (0.93, 0.3),
        
        # Result nodes
        "CollectResults": (0.5, 0.28),
        "FinalResults": (0.5, 0.22),
        "SaveCSV": (0.5, 0.15),
        "ExportCSV": (0.35, 0.08),
        "SkipExport": (0.65, 0.08),
        "End": (0.5, 0.01),
        
        # Info nodes
        "ThreadSafeLock": (0.15, 0.28),
        "MaxWorkers": (0.25, 0.48),
        "BatchSize": (0.75, 0.55),
    }
    
    # Define node colors
    colors = {
        "main": "#d4f1f9",  # Light blue for main steps
        "sub": "#e1f7d5",   # Light green for sub processes
        "concurrent": "#ffedd5",  # Light orange for concurrent processes
        "data": "#f9f9f9",  # Light gray for data flow
        "decision": "#e8eaf6"  # Light purple for decision nodes
    }
    
    # Define node borders
    borders = {
        "main": {"edgecolor": "#05668d", "linewidth": 2},
        "sub": {"edgecolor": "#43a047", "linewidth": 1},
        "concurrent": {"edgecolor": "#ff9800", "linewidth": 1},
        "data": {"edgecolor": "#9e9e9e", "linewidth": 1},
        "decision": {"edgecolor": "#3f51b5", "linewidth": 1.5}
    }
    
    # Draw nodes
    nodes = {}
    
    # Main flow nodes
    nodes["Start"] = plt.Circle(positions["Start"], 0.03, facecolor=colors["main"], **borders["main"])
    nodes["LoadCSV"] = plt.Rectangle((positions["LoadCSV"][0]-0.1, positions["LoadCSV"][1]-0.02), 0.2, 0.04, 
                               facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["CleanFile"] = plt.Rectangle((positions["CleanFile"][0]-0.1, positions["CleanFile"][1]-0.02), 0.2, 0.04, 
                                facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["ProcessData"] = plt.Rectangle((positions["ProcessData"][0]-0.1, positions["ProcessData"][1]-0.02), 0.2, 0.04, 
                                  facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["AnalyzeOrgs"] = plt.Rectangle((positions["AnalyzeOrgs"][0]-0.1, positions["AnalyzeOrgs"][1]-0.02), 0.2, 0.04, 
                                 facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["PharmaAnalysis"] = plt.Rectangle((positions["PharmaAnalysis"][0]-0.12, positions["PharmaAnalysis"][1]-0.02), 0.24, 0.04, 
                                   facecolor=colors["main"], **borders["main"], alpha=0.9)
    
    # PharmaCrew workflow
    pharma_flow = plt.Rectangle((0.1, 0.05), 0.8, 0.55, facecolor="none", edgecolor="#888888", linestyle="--", 
                  linewidth=1, alpha=0.5)
    ax.add_patch(pharma_flow)
    
    nodes["InitPharmaCrew"] = plt.Rectangle((positions["InitPharmaCrew"][0]-0.12, positions["InitPharmaCrew"][1]-0.02), 0.24, 0.04, 
                                   facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["SplitBatches"] = plt.Rectangle((positions["SplitBatches"][0]-0.12, positions["SplitBatches"][1]-0.02), 0.24, 0.04, 
                                  facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["ThreadPool"] = plt.Rectangle((positions["ThreadPool"][0]-0.15, positions["ThreadPool"][1]-0.02), 0.3, 0.04, 
                                facecolor=colors["main"], **borders["main"], alpha=0.9)
    
    # Concurrent processing nodes
    rect = plt.Rectangle((0.15, 0.25), 0.7, 0.22, facecolor="none", edgecolor="#888888", linestyle="--", 
                      linewidth=1, alpha=0.5)
    ax.add_patch(rect)
    
    nodes["Batch1"] = plt.Rectangle((positions["Batch1"][0]-0.08, positions["Batch1"][1]-0.02), 0.16, 0.04, 
                            facecolor=colors["concurrent"], **borders["concurrent"], alpha=0.9)
    nodes["Batch2"] = plt.Rectangle((positions["Batch2"][0]-0.08, positions["Batch2"][1]-0.02), 0.16, 0.04, 
                            facecolor=colors["concurrent"], **borders["concurrent"], alpha=0.9)
    nodes["Batch3"] = plt.Rectangle((positions["Batch3"][0]-0.08, positions["Batch3"][1]-0.02), 0.16, 0.04, 
                            facecolor=colors["concurrent"], **borders["concurrent"], alpha=0.9)
    nodes["BatchN"] = plt.Rectangle((positions["BatchN"][0]-0.08, positions["BatchN"][1]-0.02), 0.16, 0.04, 
                            facecolor=colors["concurrent"], **borders["concurrent"], alpha=0.9)
    
    # Batch detail nodes
    rect = plt.Rectangle((0.83, 0.25), 0.2, 0.3, facecolor="none", edgecolor="#888888", linestyle="--", 
                      linewidth=1, alpha=0.5)
    ax.add_patch(rect)
    
    nodes["CreateAgent"] = plt.Rectangle((positions["CreateAgent"][0]-0.1, positions["CreateAgent"][1]-0.015), 0.2, 0.03, 
                                 facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["CreateTask"] = plt.Rectangle((positions["CreateTask"][0]-0.1, positions["CreateTask"][1]-0.015), 0.2, 0.03, 
                                facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["CreateCrew"] = plt.Rectangle((positions["CreateCrew"][0]-0.1, positions["CreateCrew"][1]-0.015), 0.2, 0.03, 
                                facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["RunCrew"] = plt.Rectangle((positions["RunCrew"][0]-0.1, positions["RunCrew"][1]-0.015), 0.2, 0.03, 
                             facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["ProcessResults"] = plt.Rectangle((positions["ProcessResults"][0]-0.1, positions["ProcessResults"][1]-0.015), 0.2, 0.03, 
                                   facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    
    # Result nodes
    nodes["CollectResults"] = plt.Rectangle((positions["CollectResults"][0]-0.15, positions["CollectResults"][1]-0.02), 0.3, 0.04, 
                                   facecolor=colors["main"], **borders["main"], alpha=0.9)
    nodes["FinalResults"] = plt.Rectangle((positions["FinalResults"][0]-0.1, positions["FinalResults"][1]-0.02), 0.2, 0.04, 
                                  facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["SaveCSV"] = plt.Polygon([(positions["SaveCSV"][0], positions["SaveCSV"][1]+0.025), 
                                   (positions["SaveCSV"][0]-0.1, positions["SaveCSV"][1]), 
                                   (positions["SaveCSV"][0]+0.1, positions["SaveCSV"][1])], 
                            facecolor=colors["decision"], **borders["decision"], alpha=0.9)
    nodes["ExportCSV"] = plt.Rectangle((positions["ExportCSV"][0]-0.1, positions["ExportCSV"][1]-0.02), 0.2, 0.04, 
                               facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["SkipExport"] = plt.Rectangle((positions["SkipExport"][0]-0.1, positions["SkipExport"][1]-0.02), 0.2, 0.04, 
                                facecolor=colors["sub"], **borders["sub"], alpha=0.9)
    nodes["End"] = plt.Circle(positions["End"], 0.03, facecolor=colors["main"], **borders["main"])
    
    # Info nodes
    nodes["ThreadSafeLock"] = plt.Rectangle((positions["ThreadSafeLock"][0]-0.12, positions["ThreadSafeLock"][1]-0.02), 0.24, 0.04, 
                                   facecolor=colors["data"], **borders["data"], alpha=0.7)
    nodes["MaxWorkers"] = plt.Rectangle((positions["MaxWorkers"][0]-0.12, positions["MaxWorkers"][1]-0.02), 0.24, 0.04, 
                                facecolor=colors["data"], **borders["data"], alpha=0.7)
    nodes["BatchSize"] = plt.Rectangle((positions["BatchSize"][0]-0.12, positions["BatchSize"][1]-0.02), 0.24, 0.04, 
                               facecolor=colors["data"], **borders["data"], alpha=0.7)
    
    # Add all nodes to the plot
    for node in nodes.values():
        ax.add_patch(node)
    
    # Draw arrows
    def draw_arrow(start, end, **kwargs):
        kwargs.setdefault('arrowstyle', '->')
        kwargs.setdefault('linewidth', 1.5)
        kwargs.setdefault('color', '#555555')
        kwargs.setdefault('alpha', 0.8)
        
        arrow = plt.annotate('', xy=end, xytext=start, 
                         arrowprops=kwargs)
        return arrow
    
    # Main flow arrows
    draw_arrow(positions["Start"], positions["LoadCSV"])
    draw_arrow(positions["LoadCSV"], positions["CleanFile"])
    draw_arrow(positions["CleanFile"], positions["ProcessData"])
    draw_arrow(positions["ProcessData"], positions["AnalyzeOrgs"])
    draw_arrow(positions["AnalyzeOrgs"], positions["PharmaAnalysis"])
    draw_arrow(positions["PharmaAnalysis"], positions["InitPharmaCrew"])
    
    # PharmaCrew flow arrows
    draw_arrow(positions["InitPharmaCrew"], positions["SplitBatches"])
    draw_arrow(positions["SplitBatches"], positions["ThreadPool"])
    
    # Concurrent batch arrows
    draw_arrow(positions["ThreadPool"], positions["Batch1"])
    draw_arrow(positions["ThreadPool"], positions["Batch2"])
    draw_arrow(positions["ThreadPool"], positions["Batch3"])
    draw_arrow(positions["ThreadPool"], positions["BatchN"])
    
    # Batch detail arrows 
    draw_arrow((0.75, 0.4), (0.83, 0.4), linestyle=':')
    
    draw_arrow(positions["CreateAgent"], positions["CreateTask"])
    draw_arrow(positions["CreateTask"], positions["CreateCrew"])
    draw_arrow(positions["CreateCrew"], positions["RunCrew"])
    draw_arrow(positions["RunCrew"], positions["ProcessResults"])
    
    # Result connection arrows
    draw_arrow(positions["Batch1"], positions["CollectResults"])
    draw_arrow(positions["Batch2"], positions["CollectResults"])
    draw_arrow(positions["Batch3"], positions["CollectResults"])
    draw_arrow(positions["BatchN"], positions["CollectResults"])
    
    draw_arrow(positions["CollectResults"], positions["FinalResults"])
    draw_arrow(positions["FinalResults"], positions["SaveCSV"])
    draw_arrow((positions["SaveCSV"][0]-0.05, positions["SaveCSV"][1]-0.01), positions["ExportCSV"], 
            arrowstyle='->', linewidth=1)
    draw_arrow((positions["SaveCSV"][0]+0.05, positions["SaveCSV"][1]-0.01), positions["SkipExport"], 
            arrowstyle='->', linewidth=1)
    draw_arrow(positions["ExportCSV"], positions["End"])
    draw_arrow(positions["SkipExport"], positions["End"])
    
    # Info connection arrows
    draw_arrow(positions["ThreadSafeLock"], positions["CollectResults"], linestyle=':', linewidth=1, alpha=0.5)
    draw_arrow(positions["MaxWorkers"], positions["ThreadPool"], linestyle=':', linewidth=1, alpha=0.5)
    draw_arrow(positions["BatchSize"], positions["SplitBatches"], linestyle=':', linewidth=1, alpha=0.5)
    
    # Add text labels
    def add_text(pos, text, fontsize=9, **kwargs):
        kwargs.setdefault('ha', 'center')
        kwargs.setdefault('va', 'center')
        kwargs.setdefault('fontweight', 'normal')
        plt.text(pos[0], pos[1], text, fontsize=fontsize, **kwargs)
    
    # Main flow labels
    add_text(positions["Start"], "Start", fontweight='bold')
    add_text(positions["LoadCSV"], "Load CSV Data")
    add_text(positions["CleanFile"], "Clean & Validate File")
    add_text(positions["ProcessData"], "Process Attendees Data")
    add_text(positions["AnalyzeOrgs"], "Analyze Organizations")
    add_text(positions["PharmaAnalysis"], "Pharmaceutical Analysis", fontweight='bold')
    
    # Subgraph title
    add_text((0.5, 0.66), "PharmaCrew Workflow", fontsize=12, fontweight='bold')
    
    # PharmaCrew flow labels
    add_text(positions["InitPharmaCrew"], "Initialize PharmaCrew", fontweight='bold')
    add_text(positions["SplitBatches"], "Split Attendees into Batches")
    add_text(positions["ThreadPool"], "Create Thread Pool", fontweight='bold')
    
    # Concurrent processing labels
    add_text((0.5, 0.52), "Concurrent Batch Processing", fontsize=10, fontweight='bold')
    add_text(positions["Batch1"], "Batch 1")
    add_text(positions["Batch2"], "Batch 2")
    add_text(positions["Batch3"], "Batch 3")
    add_text(positions["BatchN"], "Batch N...")
    
    # Batch detail labels
    add_text((0.93, 0.55), "Batch Processing Detail", fontsize=10, fontweight='bold')
    add_text(positions["CreateAgent"], "Create Agent")
    add_text(positions["CreateTask"], "Create Task")
    add_text(positions["CreateCrew"], "Create Crew")
    add_text(positions["RunCrew"], "Execute Crew")
    add_text(positions["ProcessResults"], "Process Results")
    
    # Result labels
    add_text(positions["CollectResults"], "Collect & Combine Results", fontweight='bold')
    add_text(positions["FinalResults"], "Final Combined Results")
    add_text(positions["SaveCSV"], "Save to CSV?")
    add_text(positions["ExportCSV"], "Export to CSV")
    add_text(positions["SkipExport"], "Skip Export")
    add_text(positions["End"], "End", fontweight='bold')
    
    # Info labels
    add_text(positions["ThreadSafeLock"], "Thread-safe results\ncollection with Lock", fontsize=8)
    add_text(positions["MaxWorkers"], "Max concurrent\nworkers = 3", fontsize=8)
    add_text(positions["BatchSize"], "Configurable\nbatch size", fontsize=8)
    
    # Add diagram title
    plt.figtext(0.5, 0.98, "Conference Attendee Analysis Workflow", 
                fontsize=16, fontweight='bold', ha='center')
    
    # Add legend
    legend_x, legend_y = 0.05, 0.02
    legend_width, legend_height = 0.25, 0.18
    legend_bg = plt.Rectangle((legend_x, legend_y), legend_width, legend_height, 
                           facecolor='white', edgecolor='#888888', alpha=0.8)
    ax.add_patch(legend_bg)
    
    plt.figtext(legend_x + 0.02, legend_y + legend_height - 0.02, "Legend", 
                fontsize=10, fontweight='bold', ha='left', va='center')
    
    # Legend items
    legend_items = [
        ("Main Process", colors["main"], borders["main"]["edgecolor"]),
        ("Sub-Process", colors["sub"], borders["sub"]["edgecolor"]),
        ("Concurrent Process", colors["concurrent"], borders["concurrent"]["edgecolor"]),
        ("Data Flow", colors["data"], borders["data"]["edgecolor"]),
        ("Decision", colors["decision"], borders["decision"]["edgecolor"])
    ]
    
    for i, (label, color, border) in enumerate(legend_items):
        y_pos = legend_y + legend_height - 0.04 - (i * 0.03)
        rect = plt.Rectangle((legend_x + 0.02, y_pos - 0.01), 0.03, 0.02, 
                          facecolor=color, edgecolor=border, linewidth=1)
        ax.add_patch(rect)
        plt.figtext(legend_x + 0.06, y_pos, label, fontsize=8, ha='left', va='center')
    
    # Set tight layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig('diagrams/workflow_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Diagram created successfully: diagrams/workflow_diagram.png")

if __name__ == "__main__":
    create_workflow_diagram() 