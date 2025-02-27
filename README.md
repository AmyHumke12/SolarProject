# **Solar Production Analysis & Prediction**

## **About the Project**
This is a **hobby project** that started after I had **solar panels installed on 1/8/2024**. The process of deciding whether solar was a good investment was **far more confusing than it should have been**. Different states, electric companies, and incentives **all impact the actual value of a solar system**, and unfortunately, **not every company provides accurate projections**. 

For example, one company I met with **overestimated my electric costs over time**, making the investment look much better than it really was. Given the **high cost of solar panels**, I wanted to build something to **cut through the marketing noise and see the real numbers**.

This project has two main goals:
1. **Determine the real payoff period for my system** based on actual energy production and cost data.
2. **Explore whether solar energy production can be accurately modeled** (as a data scientist, I found this an interesting challenge).

---

## **Work in Progress**
This is an **ongoing project** with several **incomplete or exploratory components**:
- I initially **collected weather data**, which I haven't used yet. It may be useful in the future, so I haven't removed it.
- The notebooks **could be cleaned up**—there's some unnecessary processing left in place.
- The **current model is a Random Forest**, which was the **first "good enough" model** I found. Improvements will come later, but for now, my focus is **pushing the main branch to production** before refining it on a dev branch.

---

## **Features**
Currently, the project supports:

### **📡 Data Collection & Processing**
- Fetching **hourly energy production and usage** from SolarEdge.
- Pulling **historical weather data** (temperature, cloud cover, irradiance, etc.).
- Retrieving **hourly electric usage & cost data** from my electric provider.
- Aligning data to match **billing cycles** (which don’t always match calendar months).
- **General solar production estimates for my area**, merged with my personal solar data.

### **🔭 Astrological Feature Engineering**
- **Solar angle & azimuth** (tracking the position of the sun throughout the day).
- **Global tilted irradiance** (how much sunlight actually hits the panels).
- **Solar day count** (days from solstice, capturing seasonal variation).

### **🔧 Data Cleaning & Transformation**
- Converting solar & electric company data into a **consistent format**.
- Handling **missing data, time zones, and inconsistencies**.
- Computing **net energy usage, excess credits, and cost per kWh**.

### **📊 Modeling & Forecasting**
- Using **Random Forest** to predict future solar production.
- Extending historical trends to **forecast through 2034**.

### **📈 Dashboard Integration**
- Generating **summaries & visualizations** for tracking system performance.
- Displaying **payoff timeline estimates**.

---

## **Current Dependencies**
The project relies on:
```plaintext
astral, pandasql, openmeteo-requests, requests-cache, retry-requests, numpy, pandas, sqlalchemy, python-dateutil, pytz, requests, attrs, cattrs, platformdirs, url-normalize, urllib3, certifi
