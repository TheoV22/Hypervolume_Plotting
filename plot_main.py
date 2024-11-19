import argparse
from hyp_functions import *

if __name__ == '__main__':
    """
    Performs an analysis of the archive and computes hypervolume for each archive points set.
    Plots the evolution of the hypervolume according to the number of function evaluations.
    """

    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Analyze archive data and plot hypervolume evolution.")
    parser.add_argument('-pt', '--plot_type', type=int, choices=[1, 2, 3], default=2,
                        help='Type of plot you want. Choose from {1, 2, 3}. Default is 2.')
    parser.add_argument('input', nargs='+', help='Path(s) to the input folder(s).')
    args = parser.parse_args()

    # Print arguments
    print(f"Program called with arguments: \nInput folders = {args.input}")
    print(f"\nPlot type = {args.plot_type}")

    # Load and process the data
    try:
        all_files_with_hypervolume = [
            compute_cumulative_hypervolume(data, [10e9, 10e9])
            for data in load_all_datafiles(args.input)
        ]
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        exit(1)
    
    # Plot based on the chosen type
    if args.plot_type == 1:
        plot_average_hypervolume_by_function(aggregate_data_by_function(all_files_with_hypervolume))
    elif args.plot_type == 2:
        plot_average_hypervolume_by_function_dimension(aggregate_data_by_function_dimension(all_files_with_hypervolume))
    elif args.plot_type == 3:
        plot_average_hypervolume_by_dimension(aggregate_data_by_dimension(all_files_with_hypervolume))
    else:
        print(f"Invalid plot type: {args.plot_type}")
    
    # =================================================================== #
    # =========== PROMPT EXAMPLE TO RUN IN THE COMMAND LINE : =========== #
# python3 project_code/plot_main.py -pt 2 project_code/exdata/pymoo_nsga2_on_bbob-biobj/archive
    # =================================================================== #
