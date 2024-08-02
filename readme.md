# Maritime Traffic Analysis Dashboard

## Overview

This project is an interactive web application that visualizes and analyzes maritime traffic data. It uses AIS (Automatic Identification System) data to display ship movements, types, and navigational statuses.

![Screenshot 2024-08-02 201207](https://github.com/user-attachments/assets/3847a3f3-7d43-49b7-b662-993b5b654a26)

## Features

- Interactive map visualization of ship movements
- Time-based animation of ship positions
- Ship type and navigational status analysis through interactive pie charts
- Responsive design with a dark theme for enhanced visibility
- Ship selection and animation speed control
- Simulated ship movement feature

## Data Source

The project uses AIS data from the Danish Maritime Authority, available at [https://web.ais.dk/aisdata/](https://web.ais.dk/aisdata/).

## Files

- `preprocess.ipynb`: Jupyter notebook containing data preprocessing steps
- `main.py`: Main application code for the dashboard
- `merged_data.csv`: Preprocessed data file (generated from preprocessing step)
- `newship.csv`: Additional ship information data

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/mohdtalal3/Maritime-Traffic-Analysis-Dashboard.git
    ```
2. Install the required dependencies:

   ```bash
    pip install -r requirements.txt
    ```

3. Download the data and run the preprocess.ipynb file:

4. Run the the app:
   ```bash
    python main.py
    ```
5. Open a web browser and go to `http://127.0.0.1:8050/` to view the dashboard.

## Usage

- Use the dropdown menu to select ships for tracking
- Adjust the speed slider to control animation speed
- Click the Start/Stop button to control the animation
- Use the Move Ships button to simulate potential path deviations
- Interact with the pie charts to filter data based on ship types and navigational statuses

## Technologies Used

- Python
- Dash
- Plotly
- Pandas
- Dash Bootstrap Components
