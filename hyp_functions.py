#! pip3 install coco-experiment
#! pip3 install pymoo
#! pip3 install moarchiving

import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from archive_load_data import get_file_name_list, parse_archive_file_name
from moarchiving import BiobjectiveNondominatedSortedList

def read_datafile(file_path):
    # Extract metadata from the file name
    suite_name, function, instance, dimension = parse_archive_file_name(file_path)
    data = {
        "metadata": {
            "suite_name": suite_name,
            "function": function,
            "instance": instance,
            "dimension": dimension,
        },
        "data": []
    }

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Process metadata lines
            if line.startswith('%') == False:
                values = line.split()
                if values:
                    entry = {
                        "function_evaluation": int(values[0]),
                        "objective_1": float(values[1]),
                        "objective_2": float(values[2]),
                        "variable_1": float(values[3]),
                        "variable_2": float(values[4])
                    }
                    data["data"].append(entry)
    
    return data


def load_all_datafiles(path):
    all_data = []
    
    # Get list of files in the folder
    file_list = get_file_name_list(path)
    
    # Loop through each file in the list
    for file_name in file_list:
        
        # Read the data from the file and store it
        file_data = read_datafile(file_name)
        
        # Add filename to metadata for reference
        file_data["metadata"]["file_name"] = file_name
        
        # Append the data to the main list
        all_data.append(file_data)
    
    return all_data


def compute_cumulative_hypervolume(data, reference_point=[20000, 20000]):
    """
    Compute the hypervolume for each function evaluation in an archive file and append it to each entry.

    Parameters:
    - data: Output from read_datafile(), containing "data" with objectives.
    - reference_point: Reference point for hypervolume calculation (default: (5, 5)).

    Returns:
    - Updated data dictionary with hypervolume added for each function evaluation.
    """
    # Initialize a list to store non-dominated points progressively
    archive = BiobjectiveNondominatedSortedList()
    
    # Add each objective point to the archive and compute the hypervolume at each step
    for entry in data["data"]:
        objectives = [entry["objective_1"], entry["objective_2"]]
        
        # Add the point to the archive and compute the hypervolume with the current archive
        archive.add(objectives)
        hv = archive.compute_hypervolume(reference_point)
        
        # Add the computed hypervolume to the entry
        entry["hypervolume"] = float(hv)

    return data


def aggregate_data_by_function(all_files_with_hypervolume):
# Group data by function and dimension
    grouped_data = defaultdict(list)
    for data in all_files_with_hypervolume:
        func = data["metadata"]["function"]
        dim = data["metadata"]["dimension"]
        grouped_data[(func, dim)].append(data)
    return grouped_data    


def aggregate_data_by_function_dimension(all_files_with_hypervolume):
    """
    Aggregates the function evaluation and hypervolume by function and dimension,
    averaging the hypervolume values across instances for each function evaluation.
    """
    aggregated_data = defaultdict(list)

    # Iterate over the files and group by function and dimension
    for file in all_files_with_hypervolume:
        metadata = file["metadata"]
        function = metadata["function"]
        dimension = metadata["dimension"]
        
        # Extract only the relevant data: 'function_evaluation' and 'hypervolume'
        data = file["data"]
        
        for entry in data:
            aggregated_data[(function, dimension)].append({
                "function_evaluation": entry["function_evaluation"],
                "hypervolume": entry["hypervolume"]
            })

    # Now, aggregate the data for each (function, dimension) pair
    final_aggregated_data = []
    for (function, dimension), group_data in aggregated_data.items():
        # Create a DataFrame from the group data
        df = pd.DataFrame(group_data)
        
        # Group by function evaluation and calculate the mean hypervolume
        averaged_hypervolume = df.groupby("function_evaluation")["hypervolume"].mean().reset_index()

        # Store the aggregated data
        final_aggregated_data.append({
            "function": function,
            "dimension": dimension,
            "averaged_hypervolume": averaged_hypervolume
        })
    
    return final_aggregated_data


def aggregate_data_by_dimension(all_files_with_hypervolume):
    """
    Aggregates the function evaluation and hypervolume by function and dimension,
    averaging the hypervolume values across instances for each function evaluation.
    Then averages over all functions for each dimension.
    """
    aggregated_data = defaultdict(list)

    # Iterate over the files and group by function and dimension
    for file in all_files_with_hypervolume:
        metadata = file["metadata"]
        function = metadata["function"]
        dimension = metadata["dimension"]
        
        # Extract only the relevant data: 'function_evaluation' and 'hypervolume'
        data = file["data"]
        
        for entry in data:
            aggregated_data[(function, dimension)].append({
                "function_evaluation": entry["function_evaluation"],
                "hypervolume": entry["hypervolume"]
            })

    # Now, aggregate the data for each (function, dimension) pair
    final_aggregated_data = []
    for (function, dimension), group_data in aggregated_data.items():
        # Create a DataFrame from the group data
        df = pd.DataFrame(group_data)
        
        # Group by function evaluation and calculate the mean hypervolume
        averaged_hypervolume = df.groupby("function_evaluation")["hypervolume"].mean().reset_index()

        # Store the aggregated data
        final_aggregated_data.append({
            "function": function,
            "dimension": dimension,
            "averaged_hypervolume": averaged_hypervolume
        })
    
    # Now, average across all functions for each dimension
    dimension_averaged_data = defaultdict(list)
    for data in final_aggregated_data:
        dimension_averaged_data[data["dimension"]].append(data["averaged_hypervolume"])

    # Compute the average hypervolume for each dimension across all functions
    final_data_for_plotting = []
    for dimension, hypervolume_data_list in dimension_averaged_data.items():
        # Get the function evaluation points (assume all functions have the same eval points)
        function_evaluations = hypervolume_data_list[0]["function_evaluation"]
        
        # Average the hypervolume across all functions for each function evaluation
        averaged_hypervolume = pd.DataFrame(function_evaluations, columns=["function_evaluation"])
        for hypervolume_data in hypervolume_data_list:
            averaged_hypervolume["hypervolume"] = averaged_hypervolume.get("hypervolume", 0) + hypervolume_data["hypervolume"]
        
        # Divide by the number of functions to get the average
        averaged_hypervolume["hypervolume"] /= len(hypervolume_data_list)

        final_data_for_plotting.append({
            "dimension": dimension,
            "averaged_hypervolume": averaged_hypervolume
        })

    return final_data_for_plotting


def plot_average_hypervolume_by_function(aggregated_data):

    # Plot hypervolume for each function/dimension pair
    for (func, dim), datasets in aggregated_data.items():
        plt.figure(figsize=(10, 6))
        plt.title(f'Hypervolume for Function {func}, Dimension {dim}')
        plt.xlabel('Function Evaluations')
        plt.ylabel('Hypervolume')

        # Plot each instance for the given function/dimension pair
        for data in datasets:
            instance = data["metadata"]["instance"]
            evaluations = [entry["function_evaluation"] for entry in data["data"]]
            hypervolumes = [entry["hypervolume"] for entry in data["data"]]
            plt.plot(evaluations, hypervolumes, label=f'Instance {instance}')
        
        plt.legend()
        plt.show()


def plot_average_hypervolume_by_function_dimension(aggregated_data):
    """
    Plots the average hypervolume by dimension, with each function as a separate line.
    Only a subset of functions will be shown in the legend.
    """
    # Group data by dimension
    grouped_by_dimension = defaultdict(list)

    for data in aggregated_data:
        function = data["function"]
        dimension = data["dimension"]
        averaged_hypervolume = data["averaged_hypervolume"]
        
        # Group by dimension
        grouped_by_dimension[dimension].append((function, averaged_hypervolume))

    # Plotting
    for dimension, functions_data in grouped_by_dimension.items():
        plt.figure(figsize=(10, 6))
        for idx, (function, hypervolume_data) in enumerate(functions_data):
            label = None
            # Only label every 5th function to reduce clutter
            if idx % 3 == 0:
                label = f"Function {function}"
            
            # Plot the average hypervolume for each function
            plt.plot(hypervolume_data["function_evaluation"], hypervolume_data["hypervolume"], label=label)
        
        # Set the labels and title for the plot
        plt.xlabel("Function Evaluation")
        plt.ylabel("Average Hypervolume")
        plt.title(f"Average Hypervolume by Function for Dimension {dimension}")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))  # Move legend outside
        plt.grid(True)
        plt.show()


def plot_average_hypervolume_by_dimension(aggregated_data):
    """
    Plots the average hypervolume by dimension, with one line per dimension
    representing the average of all functions.
    """
    # Group data by dimension
    grouped_by_dimension = defaultdict(list)

    for data in aggregated_data:
        dimension = data["dimension"]
        averaged_hypervolume = data["averaged_hypervolume"]
        
        # Group by dimension
        grouped_by_dimension[dimension].append(averaged_hypervolume)

    # Plotting
    for dimension, hypervolume_data_list in grouped_by_dimension.items():
        plt.figure(figsize=(10, 6))
        
        # We only need to plot one line per dimension
        averaged_hypervolume = pd.DataFrame(hypervolume_data_list[0]["function_evaluation"], columns=["function_evaluation"])
        
        for hypervolume_data in hypervolume_data_list:
            averaged_hypervolume["hypervolume"] = averaged_hypervolume.get("hypervolume", 0) + hypervolume_data["hypervolume"]
        
        # Calculate the average hypervolume across all functions for each function evaluation
        averaged_hypervolume["hypervolume"] /= len(hypervolume_data_list)
        
        # Plot the average hypervolume
        plt.plot(averaged_hypervolume["function_evaluation"], averaged_hypervolume["hypervolume"], label=f"Dimension {dimension}")
        
        # Set the labels and title for the plot
        plt.xlabel("Function Evaluation")
        plt.ylabel("Average Hypervolume")
        plt.title(f"Average Hypervolume Across Functions for Dimension {dimension}")
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))  # Move legend outside
        plt.grid(True)
        plt.show()
