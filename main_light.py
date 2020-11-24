import lighting_probability
df = lighting_probability.lighting_probability_calculation()
fig = lighting_probability.chart_of_weather_probability(df)
fig.update_layout(margin=dict(l=10, r=0, t=30,b=10))