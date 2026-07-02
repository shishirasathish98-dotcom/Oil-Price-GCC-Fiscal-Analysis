import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# 1. LOAD & CLEAN DATA
# ─────────────────────────────────────────────
df = pd.read_csv('/mnt/user-data/uploads/DCOILBRENTEU.csv')
df.columns = ['Date', 'Price']
df['Date'] = pd.to_datetime(df['Date'])
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df = df.dropna()
df = df[df['Date'] >= '2018-01-01'].copy()
df = df.sort_values('Date').reset_index(drop=True)

# Monthly average
monthly = df.resample('ME', on='Date')['Price'].mean().reset_index()
monthly.columns = ['Date', 'Avg_Price']

# Annual average
annual = df.resample('YE', on='Date')['Price'].mean().reset_index()
annual['Year'] = annual['Date'].dt.year
annual.columns = ['Date', 'Avg_Price', 'Year']

print("✅ Data loaded successfully!")
print(f"   Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"   Total records: {len(df)}")
print(f"   Price range: ${df['Price'].min():.2f} - ${df['Price'].max():.2f}")

# ─────────────────────────────────────────────
# 2. OPEC+ KEY EVENTS
# ─────────────────────────────────────────────
opec_events = [
    ('2018-11-30', 'OPEC+ 1.2M\nbpd cut', 'red'),
    ('2020-04-12', 'Historic 9.7M\nbpd cut (COVID)', 'darkred'),
    ('2021-01-05', 'Saudi 1M\nbpd cut', 'orange'),
    ('2022-02-24', 'Russia-Ukraine\nWar begins', 'purple'),
    ('2022-10-05', 'OPEC+ 2M\nbpd cut', 'red'),
    ('2023-04-03', 'Surprise\nvoluntary cuts', 'brown'),
    ('2023-11-30', 'Extended cuts\ninto 2024', 'darkblue'),
]

# ─────────────────────────────────────────────
# 3. GCC FISCAL BREAKEVEN PRICES
# ─────────────────────────────────────────────
breakeven = {
    'Saudi Arabia': 76,
    'UAE':          65,
    'Qatar':        55,
    'Kuwait':       65,
    'Bahrain':      128,
    'Oman':         82,
}

# Annual avg for surplus/deficit calculation
annual_prices = {
    2018: 71.1,
    2019: 64.0,
    2020: 41.8,
    2021: 70.9,
    2022: 99.0,
    2023: 82.5,
    2024: 80.0,
    2025: 74.0,
}

# ─────────────────────────────────────────────
# 4. PLOT 1 — BRENT CRUDE PRICE TREND + OPEC EVENTS
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 7))
ax.plot(monthly['Date'], monthly['Avg_Price'], color='#1A6B8A', linewidth=2, label='Brent Crude (Monthly Avg)')
ax.fill_between(monthly['Date'], monthly['Avg_Price'], alpha=0.1, color='#1A6B8A')

for date_str, label, color in opec_events:
    date = pd.to_datetime(date_str)
    if date >= monthly['Date'].min() and date <= monthly['Date'].max():
        ax.axvline(x=date, color=color, linestyle='--', alpha=0.7, linewidth=1.2)
        price_at_date = monthly.iloc[(monthly['Date'] - date).abs().argsort()[:1]]['Avg_Price'].values[0]
        ax.annotate(label, xy=(date, price_at_date),
                   xytext=(10, 15), textcoords='offset points',
                   fontsize=7.5, color=color, fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color=color, lw=1))

ax.set_title('Brent Crude Oil Price Trend (2018–2026)\nwith OPEC+ Key Decision Events', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Date', fontsize=11)
ax.set_ylabel('Price (USD/Barrel)', fontsize=11)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('white')
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/1_brent_price_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 1 saved: Brent Price Trend")

# ─────────────────────────────────────────────
# 5. PLOT 2 — ANNUAL PRICE VOLATILITY
# ─────────────────────────────────────────────
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
volatility = df.groupby('Year')['Price'].std().reset_index()
volatility.columns = ['Year', 'Volatility']
avg_by_year = df.groupby('Year')['Price'].mean().reset_index()
avg_by_year.columns = ['Year', 'Avg_Price']

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Avg price by year
colors = ['#c0392b' if p < 65 else '#27ae60' if p > 80 else '#f39c12' 
          for p in avg_by_year['Avg_Price']]
bars = axes[0].bar(avg_by_year['Year'].astype(str), avg_by_year['Avg_Price'], 
                    color=colors, edgecolor='white', linewidth=0.5)
for bar, val in zip(bars, avg_by_year['Avg_Price']):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'${val:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[0].set_title('Average Annual Brent Crude Price\n(2018–2026)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('USD/Barrel')
axes[0].grid(axis='y', alpha=0.3)
axes[0].set_facecolor('#f8f9fa')
legend_elements = [mpatches.Patch(color='#c0392b', label='< $65 (Low)'),
                   mpatches.Patch(color='#f39c12', label='$65-$80 (Moderate)'),
                   mpatches.Patch(color='#27ae60', label='> $80 (High)')]
axes[0].legend(handles=legend_elements, fontsize=8)

# Volatility by year
axes[1].bar(volatility['Year'].astype(str), volatility['Volatility'],
            color='#8e44ad', edgecolor='white', linewidth=0.5)
for i, (year, vol) in enumerate(zip(volatility['Year'], volatility['Volatility'])):
    axes[1].text(i, vol + 0.2, f'{vol:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
axes[1].set_title('Annual Price Volatility (Std Dev)\n(2018–2026)', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Year'); axes[1].set_ylabel('Standard Deviation (USD)')
axes[1].grid(axis='y', alpha=0.3)
axes[1].set_facecolor('#f8f9fa')

plt.suptitle('Oil Price Analysis: Annual Averages & Volatility', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/2_annual_volatility.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 2 saved: Annual Volatility")

# ─────────────────────────────────────────────
# 6. PLOT 3 — GCC FISCAL BREAKEVEN COMPARISON
# ─────────────────────────────────────────────
years = list(range(2018, 2026))
actual_prices = [annual_prices[y] for y in years]

fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(years, actual_prices, 'o-', color='#1A6B8A', linewidth=2.5,
        markersize=8, label='Actual Brent Price', zorder=5)

colors_be = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12', '#9b59b6', '#1abc9c']
for (country, be_price), color in zip(breakeven.items(), colors_be):
    ax.axhline(y=be_price, color=color, linestyle='--', alpha=0.8, linewidth=1.5)
    ax.text(2025.1, be_price, f'{country}\n${be_price}', 
            fontsize=8.5, color=color, fontweight='bold', va='center')

ax.set_title('Brent Crude Price vs GCC Fiscal Breakeven Prices (2018–2026)\nAbove line = Budget Surplus | Below line = Budget Deficit',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('USD per Barrel', fontsize=11)
ax.set_xticks(years)
ax.grid(True, alpha=0.3)
ax.set_facecolor('#f8f9fa')
ax.legend(fontsize=10, loc='upper left')
ax.set_xlim(2017.5, 2026)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/3_gcc_breakeven_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 3 saved: GCC Breakeven Comparison")

# ─────────────────────────────────────────────
# 7. PLOT 4 — SURPLUS/DEFICIT HEATMAP
# ─────────────────────────────────────────────
countries = list(breakeven.keys())
heatmap_data = []
for country in countries:
    row = []
    be = breakeven[country]
    for year in years:
        actual = annual_prices[year]
        row.append(round(actual - be, 1))
    heatmap_data.append(row)

heatmap_df = pd.DataFrame(heatmap_data, index=countries, columns=years)

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(heatmap_df, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
            linewidths=0.5, ax=ax, cbar_kws={'label': 'USD/Barrel (Surplus +ve / Deficit -ve)'})
ax.set_title('GCC Country Fiscal Surplus/Deficit vs Oil Price (2018–2026)\n(Positive = Surplus, Negative = Deficit)',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Country', fontsize=11)

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/4_gcc_surplus_deficit_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ Chart 4 saved: Surplus/Deficit Heatmap")

# ─────────────────────────────────────────────
# 8. SUMMARY STATS
# ─────────────────────────────────────────────
print("\n" + "="*50)
print("📊 KEY FINDINGS SUMMARY")
print("="*50)
print(f"Average Brent Price (2018-2026): ${df['Price'].mean():.2f}/barrel")
print(f"Highest Price: ${df['Price'].max():.2f} on {df.loc[df['Price'].idxmax(), 'Date'].date()}")
print(f"Lowest Price:  ${df['Price'].min():.2f} on {df.loc[df['Price'].idxmin(), 'Date'].date()}")
print(f"Most Volatile Year: {volatility.loc[volatility['Volatility'].idxmax(), 'Year']}")
print(f"Most Stable Year:   {volatility.loc[volatility['Volatility'].idxmin(), 'Year']}")
print(f"\nGCC Breakeven Analysis:")
for country, be in breakeven.items():
    surplus_years = [y for y in years if annual_prices[y] > be]
    deficit_years = [y for y in years if annual_prices[y] <= be]
    print(f"  {country}: {len(surplus_years)} surplus years, {len(deficit_years)} deficit years")
print("\n✅ All charts saved to outputs folder!")
