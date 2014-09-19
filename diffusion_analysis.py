'''
Author: Tyler Reddy

The purpose of this Python module is to provide utility functions for analyzing the diffusion of particles in molecular dynamics simulation trajectories using either linear or anomalous diffusion models.'''

def fit_anomalous_diffusion_data(time_data_array,MSD_data_array,degrees_of_freedom=2):
    '''This function should fit anomalous diffusion data to Equation 1 in Kneller et al. (2011) J Chem Phys 135: 141105. It will assign an appropriate coefficient based on the specified degrees_of_freedom. The latter value defaults to 2 (i.e., a planar phospholipid bilayer).
    Input data should include arrays of MSD (in Angstroms) and time values (in ns).
    The results are returned in a tuple.
    Returns
    -------
    fractional_diffusion_coefficient
        The fractional diffusion coefficient (units of Angstrom ** 2 / ns ** alpha)
    standard_deviation_fractional_diffusion_coefficient
        The standard deviation of the fractional diffusion coefficent (units of Angstrom ** 2 / ns ** alpha)
    alpha
        The scaling exponent (no dimensions) of the non-linear fit
    standard_deviation_alpha
        The standard deviation of the scaling exponent (no dimensions)
        '''

    def function_to_fit(time,fractional_diffusion_coefficient,scaling_exponent):
        coefficient_dictionary = {1:2,2:4,3:6} #dictionary for mapping degrees_of_freedom to coefficient in fitting equation
        coefficient = coefficient_dictionary[degrees_of_freedom]
        return coefficient * fractional_diffusion_coefficient * (time ** scaling_exponent) #equation 1 in the above paper with appropriate coefficient based on degrees of freedom

    #fit the above function to the data and pull out the resulting parameters
    optimized_parameter_value_array, estimated_covariance_params_array = scipy.optimize.curve_fit(function_to_fit,time_data_array,MSD_data_array)
    #generate sample fitting data over the range of time window values (user can plot if they wish)
    sample_fitting_data_X_values_nanoseconds = numpy.linspace(time_data_array[0],time_data_array[-1],100)
    sample_fitting_data_Y_values_Angstroms = function_to_fit(sample_fitting_data_X_values_nanoseconds, *optimized_parameter_value_array)
    #could then plot the non-linear fit curve in matplotlib with, for example: axis.plot(sample_fitting_data_X_values_nanoseconds,sample_fitting_data_Y_values_Angstroms,color='black')
    #could plot the original data points alongside the fit (MSD vs time) with, for example: axis.scatter(time_data_array,MSD_data_array,color='black')

    #extract pertinent values from the scipy curve_fit arrays (D_alpha, alpha, and their standard deviations)
    parameter_standard_deviation_array = numpy.sqrt(numpy.diagonal(estimated_covariance_params_array))
    fractional_diffusion_coefficient = optimized_parameter_value_array[0]
    standard_deviation_fractional_diffusion_coefficient = parameter_standard_deviation_array[0]
    alpha = optimized_parameter_value_array[1]
    standard_deviation_alpha = parameter_standard_deviation_array[1]

    return (fractional_diffusion_coefficient, standard_deviation_fractional_diffusion_coefficient, alpha, standard_deviation_alpha,sample_fitting_data_X_values_nanoseconds,sample_fitting_data_Y_values_Angstroms)

def fit_linear_diffusion_data(time_data_array,MSD_data_array,index_window_filter):
    '''The (crude) linear MSD vs. time slope = diffusion constant approach and the error estimate used by g_msd.'''
    x_data_array = time_data_array[index_window_filter:]
    y_data_array = MSD_data_array[index_window_filter:]
    slope, intercept = numpy.polyfit(x_data_array,y_data_array,1)
    diffusion_constant = slope / (4 * 10 ** 7) #convert to standard cm ^ 2 / s units
    #estimate error in D constant using g_msd approach
    first_half_x_data, second_half_x_data = numpy.array_split(x_data_array,2)
    first_half_y_data, second_half_y_data = numpy.array_split(y_data_array,2)
    slope_first_half, intercept_first_half = numpy.polyfit(first_half_x_data,first_half_y_data,1)
    slope_second_half, intercept_second_half = numpy.polyfit(second_half_x_data,second_half_y_data,1)
    diffusion_constant_error_estimate = abs(slope_first_half - slope_second_half) / (4 * 10 ** 7)
    #I've plotted the linear stuff previously so not going to worry about that here, at least for now
    log_x_data_array = numpy.log10(x_data_array)
    log_y_data_array = numpy.log10(y_data_array)
    slope, intercept = numpy.polyfit(log_x_data_array,log_y_data_array,1)
    scaling_exponent = slope
    return (diffusion_constant, diffusion_constant_error_estimate, scaling_exponent)



