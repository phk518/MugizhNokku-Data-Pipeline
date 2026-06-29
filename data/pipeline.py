import numpy as np

def generate_mock_layer(sst_shift: float, moisture_mult: float):
    """
    Generates geospatial coordinate projections mapped around the Western Ghats.
    Handles coordinate grid interpolation calculations locally using Ramanujan chaos formulations.
    Returns: (tensor_payload, max_intensity, average_intensity)
    """
    # Formulate coordinate framework covering the Western Ghats boundary (High-Res)
    lats = np.linspace(8.5, 16.0, 150)
    lons = np.linspace(73.5, 77.5, 150)
    
    # Vectorized Grid Matrix Instantiation
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    N = 16.0 * 77.5 # Normalization factor based on coordinate bounding box
    
    # Generate spatial high-frequency fractal noise
    noise_1 = np.sin(lat_grid * 20.0) * np.cos(lon_grid * 20.0)
    noise_2 = np.sin(lat_grid * 45.0 + 1.5) * np.cos(lon_grid * 45.0 - 0.5)
    fractal_noise = noise_1 + (0.5 * noise_2)
    
    # Ramanujan q(x, y) Parameter Formulation with embedded spatial noise
    q_xy = np.tanh(((lat_grid * lon_grid / N) + fractal_noise * 0.25) * moisture_mult) * np.exp(-0.07 * sst_shift)
    
    # Bottom-Up Continued Fraction Evaluation (Depth d=10)
    K_xy = np.zeros_like(q_xy)
    for i in range(10, 0, -1):
        K_xy = (q_xy ** i) / (1.0 + K_xy)
        
    # Predictive Tensor Synthesis
    R_base = np.sin(lat_grid * 0.5) * np.cos(lon_grid * 0.5) * 5.0 + 5.0
    lambda_coef = 15.0 # Scaling coefficient for micro-turbulence depth
    
    # Synthesize base, chaotic convergence factor, and micro-turbulence
    R_pred = R_base * np.exp(0.07 * sst_shift) * moisture_mult + (lambda_coef * K_xy)
    R_pred += fractal_noise * K_xy * 25.0 # Amplify turbulence based on convergence
    R_pred = np.maximum(0.0, R_pred)
    
    # Vectorized payload generation (dropping flat background to reveal localized fractal clusters)
    mask = R_pred > 15.0
    tensor_payload = np.column_stack((lat_grid[mask], lon_grid[mask], R_pred[mask])).tolist()
                
    # Recalculate readout bounds dynamically
    vals = [pt[2] for pt in tensor_payload]
    
    if vals:
        max_val = f"{int(np.max(vals))}%"
        mean_val = f"{np.mean(vals):.1f} mm"
    else:
        max_val = "0%"
        mean_val = "0.0 mm"
        
    return tensor_payload, max_val, mean_val
