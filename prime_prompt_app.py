
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

@st.cache_data
def load_multiplier_data(csv_path: str) -> pd.DataFrame:
    """
    Loads the CSV data into a DataFrame.
    Assumes:
      - Column 0 = 'day'
      - Column 1 = 'some_int'
      - Column 2 = 'multiplier'
    """
    df = pd.read_csv(csv_path, header=None)
    df.columns = ['day', 'int_col', 'multiplier']  # rename for clarity
    return df

def calculate_roi(token1_price, token2_price, day_multiplier):
    """
    Calculate ROI values given:
      - token1_price: Price of Token 1 (holding value)
      - token2_price: Price of Token 2
      - day_multiplier: The multiplier looked up from the table based on 'days locked up'
    
    For demonstration, we treat '396' as a baseline total Token2 reward when the multiplier=1.
    Then if the multiplier is e.g. 9.615405784, your total Token2 is 396 * 9.615405784.
    """
    holding_value = token1_price
    # total_token2_reward = 396 * day_multiplier
    #
    # Or, if you had logic that originally used 396 for “113 weeks” 
    # but now want partial calculations, adapt as needed. For simplicity,
    # we’ll just do the above direct multiplication:
    total_token2_reward = 396 * day_multiplier
    
    locking_value = total_token2_reward * token2_price
    roi_ratio = 0
    if holding_value != 0:
        roi_ratio = locking_value / holding_value
    
    return holding_value, locking_value, roi_ratio

def main():
    st.title("ROI Comparison: Holding vs. Locking with Day-Based Multiplier")
    
    # 1) Load the multiplier data from CSV
    #    Make sure you've placed 'multipliers.csv' in the same directory or update the path as needed.
    df = load_multiplier_data('multipliers.csv')
    
    # Determine the min and max day from the dataset
    min_day = int(df['day'].min())
    max_day = int(df['day'].max())
    
    # 2) Create the Streamlit sliders:
    token1_price = st.slider("Token1 Price ($)", 0.5, 15.0, 2.94, step=0.1)
    token2_price = st.slider("Token2 Price ($)", 0.10, 1.5, 0.5, step=0.05)
    
    # Instead of the old multiplier slider, we now have:
    chosen_day = st.slider("Days Locked Up", min_day, max_day, 113, step=1)
    
    # 3) Lookup the multiplier from the DataFrame for the chosen day
    #    (We assume there's exactly one row per 'day'.)
    row = df.loc[df['day'] == chosen_day]
    if len(row) == 0:
        st.error(f"No matching row found for day={chosen_day}")
        return
    
    day_multiplier = float(row['multiplier'].iloc[0])
    
    # 4) Calculate ROI using the day-based multiplier
    holding_value, locking_value, roi_ratio = calculate_roi(token1_price, token2_price, day_multiplier)
    
    # Display computed values
    st.write(f"**Token 1 Price:** ${token1_price:.2f}")
    st.write(f"**Token 2 Price:** ${token2_price:.2f}")
    st.write(f"**Chosen Day (Locked):** {chosen_day}")
    st.write(f"**Day's Multiplier:** {day_multiplier:.6f}")
    st.write("")
    st.write(f"**Holding Value (Token1):** ${holding_value:.2f}")
    st.write(f"**Locking Value (396 × day_multiplier × Token2 Price):** ${locking_value:.2f}")
    st.write(f"**ROI (Locking / Holding):** {roi_ratio:.2f}")
    
    if roi_ratio > 1:
        st.write("**Result:** Locking produces a higher ROI than holding.")
    elif roi_ratio < 1:
        st.write("**Result:** Holding is more profitable than locking.")
    else:
        st.write("**Result:** The strategies are at break-even.")
    
    # 5) Create a bar chart for visual comparison
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ['Holding Token1', 'Locking Token1']
    values = [holding_value, locking_value]
    bars = ax.bar(labels, values, color=['steelblue', 'seagreen'])
    
    ax.set_ylabel('Dollar Value per Token1')
    ax.set_title('ROI Comparison: Holding vs. Locking')
    
    # Annotate bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'${height:.2f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Give some padding on the top so text doesn’t collide
    ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)
    
    # Annotate with the day + multiplier
    annotation = f"Day: {chosen_day}\nMultiplier: {day_multiplier:.4f}"
    ax.text(0.05, 0.90, annotation, transform=ax.transAxes, 
            fontsize=9, color='black', ha='left', va='top',
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))
    
    st.pyplot(fig)

if __name__ == "__main__":
    main()
