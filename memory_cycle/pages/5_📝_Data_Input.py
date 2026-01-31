"""Data input page for manual entry and CSV upload."""

import streamlit as st
import pandas as pd
import yaml
from pathlib import Path
import sys
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import DataLoader, DataValidator

st.set_page_config(page_title="Data Input", page_icon="📝", layout="wide")

st.title("📝 Data Input")
st.markdown("Manual data entry and CSV upload")

# Data directory
data_dir = Path(__file__).parent.parent / 'data'
data_dir.mkdir(exist_ok=True)

# Initialize loader
loader = DataLoader(data_dir)

# Tabs for different input methods
tab1, tab2, tab3 = st.tabs(["Manual Entry", "CSV Upload", "Current Data"])

# Tab 1: Manual Entry
with tab1:
    st.subheader("Enter Quarterly Data")

    st.markdown("""
    Enter the latest quarterly market metrics. All fields are required for the model to function properly.
    """)

    with st.form("quarterly_data_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input(
                "Quarter End Date",
                value=datetime.now(),
                help="Last day of the quarter"
            )

            dram_price = st.number_input(
                "DRAM Contract Price Index",
                min_value=0.0,
                value=100.0,
                step=1.0,
                help="Indexed to Q1 2015 = 100"
            )

            dram_spot = st.number_input(
                "DRAM Spot Index",
                min_value=0.0,
                value=100.0,
                step=1.0,
                help="Spot price index"
            )

            hbm_asp = st.number_input(
                "HBM ASP ($/GB)",
                min_value=0.0,
                value=30.0,
                step=0.1,
                help="HBM average selling price per GB"
            )

            inventory = st.number_input(
                "Inventory Weeks (Supplier)",
                min_value=0.0,
                value=12.0,
                step=0.1,
                help="Weeks of DRAM inventory at suppliers"
            )

        with col2:
            utilization = st.number_input(
                "Utilization Rate",
                min_value=0.0,
                max_value=1.0,
                value=0.85,
                step=0.01,
                format="%.2f",
                help="Fab utilization rate (0-1)"
            )

            capex = st.number_input(
                "Quarterly Capex ($B)",
                min_value=0.0,
                value=5.0,
                step=0.1,
                help="Combined big-3 quarterly capex in billions USD"
            )

            hbm_share = st.number_input(
                "HBM Revenue Share (%)",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=0.1,
                help="HBM as % of total DRAM revenue"
            )

            nvidia_rev = st.number_input(
                "Nvidia Datacenter Revenue ($B)",
                min_value=0.0,
                value=10.0,
                step=0.1,
                help="Nvidia datacenter revenue as AI proxy"
            )

            dram_revenue = st.number_input(
                "Total DRAM Revenue ($B)",
                min_value=0.0,
                value=25.0,
                step=0.1,
                help="Total DRAM industry revenue"
            )

        source_notes = st.text_area(
            "Source Notes (optional)",
            placeholder="Record your data sources for audit trail...",
            help="Document where you got this data"
        )

        submitted = st.form_submit_button("Add Data Point", type="primary")

        if submitted:
            # Validate
            new_data = {
                'date': pd.to_datetime(date),
                'dram_contract_price_index': dram_price,
                'dram_spot_index': dram_spot,
                'hbm_asp_estimate_usd_per_gb': hbm_asp,
                'inventory_weeks_supplier': inventory,
                'utilization_rate': utilization,
                'capex_quarterly_bn_usd': capex,
                'hbm_revenue_share_pct': hbm_share,
                'nvidia_datacenter_rev_bn_usd': nvidia_rev,
                'dram_revenue_bn_usd': dram_revenue
            }

            is_valid, error_msg = DataValidator.validate_quarterly_input(new_data)

            if is_valid:
                # Load existing data
                try:
                    df = loader.load_historical_data()
                except:
                    df = loader._create_empty_dataframe()

                # Add new row
                new_row = pd.DataFrame([new_data]).set_index('date')
                df = pd.concat([df, new_row])
                df = df[~df.index.duplicated(keep='last')]  # Remove duplicates, keep latest
                df.sort_index(inplace=True)

                # Save
                loader.save_historical_data(df)

                st.success(f"✅ Data point for {date} added successfully!")

                # Log source notes if provided
                if source_notes:
                    notes_file = data_dir / 'source_notes.txt'
                    with open(notes_file, 'a') as f:
                        f.write(f"\n{date}: {source_notes}\n")

            else:
                st.error(f"❌ Validation error: {error_msg}")

# Tab 2: CSV Upload
with tab2:
    st.subheader("Upload Historical Data")

    st.markdown("""
    Upload a CSV file with historical quarterly data. The file should have the following columns:

    - `date`: Quarter end date (YYYY-MM-DD)
    - `dram_contract_price_index`: Indexed DRAM contract price
    - `dram_spot_index`: Indexed DRAM spot price
    - `hbm_asp_estimate_usd_per_gb`: HBM ASP estimate
    - `inventory_weeks_supplier`: Weeks of inventory
    - `utilization_rate`: Fab utilization (0-1)
    - `capex_quarterly_bn_usd`: Quarterly capex
    - `hbm_revenue_share_pct`: HBM revenue share
    - `nvidia_datacenter_rev_bn_usd`: Nvidia datacenter revenue
    - `dram_revenue_bn_usd`: Total DRAM revenue

    Download the template to see the expected format.
    """)

    # Template download
    template_data = {
        'date': ['2024-12-31'],
        'dram_contract_price_index': [100.0],
        'dram_spot_index': [100.0],
        'hbm_asp_estimate_usd_per_gb': [30.0],
        'inventory_weeks_supplier': [12.0],
        'utilization_rate': [0.85],
        'capex_quarterly_bn_usd': [5.0],
        'hbm_revenue_share_pct': [20.0],
        'nvidia_datacenter_rev_bn_usd': [10.0],
        'dram_revenue_bn_usd': [25.0]
    }
    template_df = pd.DataFrame(template_data)

    st.download_button(
        label="Download Template CSV",
        data=template_df.to_csv(index=False),
        file_name="historical_data_template.csv",
        mime="text/csv"
    )

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload historical data CSV"
    )

    if uploaded_file is not None:
        try:
            # Read CSV
            uploaded_df = pd.read_csv(uploaded_file, parse_dates=['date'])

            # Validate columns
            required_cols = [
                'date', 'dram_contract_price_index', 'inventory_weeks_supplier',
                'utilization_rate'
            ]

            missing_cols = [col for col in required_cols if col not in uploaded_df.columns]

            if missing_cols:
                st.error(f"❌ Missing required columns: {missing_cols}")
            else:
                st.success("✅ File validated successfully!")

                # Preview
                st.subheader("Data Preview")
                st.dataframe(uploaded_df.head(10), use_container_width=True)

                # Statistics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Quarters", len(uploaded_df))

                with col2:
                    st.metric("Date Range Start", uploaded_df['date'].min().strftime('%Y-%m-%d'))

                with col3:
                    st.metric("Date Range End", uploaded_df['date'].max().strftime('%Y-%m-%d'))

                # Confirm upload
                if st.button("Confirm Upload", type="primary"):
                    # Set date as index
                    uploaded_df.set_index('date', inplace=True)
                    uploaded_df.sort_index(inplace=True)

                    # Save
                    loader.save_historical_data(uploaded_df)

                    st.success("✅ Data uploaded successfully!")
                    st.balloons()

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.exception(e)

    # Regime labels upload
    st.markdown("---")
    st.subheader("Upload Regime Labels (Optional)")

    st.markdown("""
    Upload ground truth regime labels for validation. CSV should have:
    - `date`: Quarter end date
    - `regime`: 'tight', 'balanced', or 'glut'
    - `confidence`: Confidence in label (0-1)
    - `notes`: Optional context
    """)

    labels_file = st.file_uploader(
        "Choose regime labels CSV",
        type=['csv'],
        key='labels_upload'
    )

    if labels_file is not None:
        try:
            labels_df = pd.read_csv(labels_file, parse_dates=['date'])

            if 'date' in labels_df.columns and 'regime' in labels_df.columns:
                st.success("✅ Regime labels validated!")
                st.dataframe(labels_df.head(10), use_container_width=True)

                if st.button("Upload Regime Labels", type="primary"):
                    labels_path = data_dir / 'regime_labels.csv'
                    labels_df.to_csv(labels_path, index=False)
                    st.success("✅ Regime labels uploaded successfully!")

            else:
                st.error("❌ File must contain 'date' and 'regime' columns")

        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Tab 3: View Current Data
with tab3:
    st.subheader("Current Historical Data")

    try:
        df = loader.load_historical_data()

        if df.empty:
            st.info("No data loaded yet. Please add data using Manual Entry or CSV Upload.")
        else:
            st.success(f"✅ {len(df)} quarters of data loaded")

            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Quarters", len(df))

            with col2:
                st.metric("Start Date", df.index.min().strftime('%Y-%m-%d'))

            with col3:
                st.metric("End Date", df.index.max().strftime('%Y-%m-%d'))

            with col4:
                st.metric("Completeness", f"{df.notna().mean().mean() * 100:.0f}%")

            # Data table
            st.markdown("---")
            st.subheader("Full Dataset")

            st.dataframe(
                df.style.format({
                    'dram_contract_price_index': '{:.1f}',
                    'dram_spot_index': '{:.1f}',
                    'hbm_asp_estimate_usd_per_gb': '{:.1f}',
                    'inventory_weeks_supplier': '{:.1f}',
                    'utilization_rate': '{:.2f}',
                    'capex_quarterly_bn_usd': '{:.1f}',
                    'hbm_revenue_share_pct': '{:.1f}',
                    'nvidia_datacenter_rev_bn_usd': '{:.1f}',
                    'dram_revenue_bn_usd': '{:.1f}'
                }),
                use_container_width=True
            )

            # Export
            st.markdown("---")
            st.subheader("Export Data")

            csv = df.reset_index().to_csv(index=False)

            st.download_button(
                label="Download Current Data as CSV",
                data=csv,
                file_name=f"historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

            # Delete data option
            st.markdown("---")
            st.subheader("⚠️ Danger Zone")

            with st.expander("Delete All Data"):
                st.warning("This will permanently delete all historical data. This action cannot be undone.")

                confirm_delete = st.text_input(
                    "Type 'DELETE' to confirm",
                    key='delete_confirm'
                )

                if st.button("Delete All Data", type="secondary"):
                    if confirm_delete == "DELETE":
                        data_file = data_dir / 'historical_data.csv'
                        if data_file.exists():
                            data_file.unlink()
                        st.success("✅ All data deleted")
                        st.rerun()
                    else:
                        st.error("❌ Confirmation text does not match")

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.exception(e)

    # Regime labels
    st.markdown("---")
    st.subheader("Regime Labels")

    try:
        labels = loader.load_regime_labels()

        if labels.empty:
            st.info("No regime labels loaded.")
        else:
            st.success(f"✅ {len(labels)} regime labels loaded")
            st.dataframe(labels, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading regime labels: {str(e)}")
