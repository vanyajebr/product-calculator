import streamlit as st
import pandas as pd

def calculate_heizlastberechnung(area_m2):
    """Calculate Heizlastberechnung price with 20% iSFP discount"""
    if area_m2 <= 150:
        original_price = 900
        discounted_price = 720  # 20% discount applied
    elif area_m2 <= 250:
        original_price = 1250
        discounted_price = 1000  # 20% discount applied
    else:
        original_price = 1000 + (4 * area_m2)
        discounted_price = original_price * 0.8  # 20% discount applied
    
    return original_price, discounted_price

def calculate_hydraulischer_abgleich(area_m2):
    """Calculate Hydraulischer Abgleich price with 20% iSFP discount"""
    if area_m2 <= 150:
        original_price = 800
        discounted_price = 640  # 20% discount applied
    elif area_m2 <= 250:
        original_price = 900
        discounted_price = 720  # 20% discount applied
    else:
        original_price = 900 + (4 * area_m2)
        discounted_price = original_price * 0.8  # 20% discount applied
    
    return original_price, discounted_price

def calculate_isfp(wohneinheiten):
    """Calculate iSFP price with built-in subsidies"""
    if wohneinheiten <= 2:
        original_price = 1300
        subsidy = 650
    elif wohneinheiten <= 9:
        original_price = 1700
        subsidy = 850
    elif wohneinheiten <= 19:
        original_price = 2290
        subsidy = 850
    elif wohneinheiten <= 29:
        original_price = 3940
        subsidy = 850
    elif wohneinheiten <= 49:
        original_price = 4940
        subsidy = 850
    else:
        original_price = 5940
        subsidy = 850
    
    final_price = original_price - subsidy
    return original_price, final_price, subsidy

def calculate_antragstellung(wohneinheiten, typ):
    """Calculate Antragstellung Einzelmaßnahme price"""
    if typ == "Heizung":
        if wohneinheiten == 1:
            base_amount = 30000
        elif wohneinheiten <= 6:
            base_amount = 30000 + ((wohneinheiten - 1) * 15000)
        else:
            base_amount = 30000 + (5 * 15000) + ((wohneinheiten - 6) * 8000)
    else:  # Other
        if wohneinheiten <= 11:
            base_amount = 60000 * wohneinheiten
        else:
            base_amount = 660000  # Limit reached
    
    calculated_price = base_amount * 0.03
    return calculated_price

def main():
    st.title("🧮 Product Bundle Calculator")
    st.markdown("---")
    
    # Input section
    st.header("📋 Input Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        wohneinheiten = st.number_input("Number of Wohneinheiten", min_value=1, value=1, step=1)
    
    with col2:
        area_m2 = st.number_input("Area (m²)", min_value=1, value=100, step=1)
    
    # Einzelmaßnahmen section
    st.header("🔧 Einzelmaßnahmen")
    
    # Initialize session state for einzelmassnahmen
    if 'einzelmassnahmen' not in st.session_state:
        st.session_state.einzelmassnahmen = []
    
    # Add new einzelmaßnahme
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        new_typ = st.selectbox("Select Type", ["Heizung", "Other"], key="new_typ")
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("Add Einzelmaßnahme"):
            st.session_state.einzelmassnahmen.append(new_typ)
            st.rerun()
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("Clear All"):
            st.session_state.einzelmassnahmen = []
            st.rerun()
    
    # Display added einzelmaßnahmen
    if st.session_state.einzelmassnahmen:
        st.subheader("Added Einzelmaßnahmen:")
        for i, typ in enumerate(st.session_state.einzelmassnahmen):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{i+1}. {typ}")
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.einzelmassnahmen.pop(i)
                    st.rerun()
    
    st.markdown("---")
    
    # Calculate button
    if st.button("💰 Calculate Total Price", type="primary"):
        # Calculate all products
        
        # 1. Heizlastberechnung
        heiz_original, heiz_discounted = calculate_heizlastberechnung(area_m2)
        heiz_forderung = heiz_discounted * 0.5
        heiz_final = heiz_discounted - heiz_forderung
        
        # 2. Hydraulischer Abgleich
        hydr_original, hydr_discounted = calculate_hydraulischer_abgleich(area_m2)
        hydr_forderung = hydr_discounted * 0.5
        hydr_final = hydr_discounted - hydr_forderung
        
        # 3. iSFP
        isfp_original, isfp_final, isfp_subsidy = calculate_isfp(wohneinheiten)
        
        # 4. Antragstellung Einzelmaßnahmen
        antrag_total_original = 0
        antrag_total_forderung = 0
        antrag_details = []
        
        for typ in st.session_state.einzelmassnahmen:
            antrag_price = calculate_antragstellung(wohneinheiten, typ)
            antrag_forderung = antrag_price * 0.5
            antrag_final = antrag_price - antrag_forderung
            
            antrag_total_original += antrag_price
            antrag_total_forderung += antrag_forderung
            
            antrag_details.append({
                'Type': typ,
                'Original Price': f"€{antrag_price:.2f}",
                'Forderung': f"€{antrag_forderung:.2f}",
                'Final Price': f"€{antrag_final:.2f}"
            })
        
        antrag_total_final = antrag_total_original - antrag_total_forderung
        
        # Calculate totals
        total_original = heiz_original + hydr_original + isfp_original + antrag_total_original
        total_discounts = (heiz_original - heiz_discounted) + (hydr_original - hydr_discounted)
        total_forderung = heiz_forderung + hydr_forderung + isfp_subsidy + antrag_total_forderung
        total_full_price = heiz_discounted + hydr_discounted + isfp_final + antrag_total_original
        total_user_pays = heiz_final + hydr_final + isfp_final + antrag_total_final
        
        # Display results
        st.header("📊 Calculation Results")
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Full Price", f"€{total_full_price:.2f}", 
                     delta=f"-€{total_discounts:.2f} (iSFP discount)")
        
        with col2:
            st.metric("User Pays", f"€{total_user_pays:.2f}")
        
        with col3:
            st.metric("Forderung Subsidy", f"€{total_forderung:.2f}")
        
        # Detailed breakdown
        st.subheader("📋 Detailed Breakdown")
        
        breakdown_data = [
            {
                'Product': 'Heizlastberechnung',
                'Original Price': f"€{heiz_original:.2f}",
                'After iSFP Discount': f"€{heiz_discounted:.2f}",
                'Forderung': f"€{heiz_forderung:.2f}",
                'Final Price': f"€{heiz_final:.2f}"
            },
            {
                'Product': 'Hydraulischer Abgleich',
                'Original Price': f"€{hydr_original:.2f}",
                'After iSFP Discount': f"€{hydr_discounted:.2f}",
                'Forderung': f"€{hydr_forderung:.2f}",
                'Final Price': f"€{hydr_final:.2f}"
            },
            {
                'Product': 'iSFP',
                'Original Price': f"€{isfp_original:.2f}",
                'After iSFP Discount': f"€{isfp_original:.2f}",
                'Forderung': f"€{isfp_subsidy:.2f}",
                'Final Price': f"€{isfp_final:.2f}"
            }
        ]
        
        # Add Antragstellung details
        for i, detail in enumerate(antrag_details):
            breakdown_data.append({
                'Product': f"Antragstellung {detail['Type']} #{i+1}",
                'Original Price': detail['Original Price'],
                'After iSFP Discount': detail['Original Price'],
                'Forderung': detail['Forderung'],
                'Final Price': detail['Final Price']
            })
        
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        


if __name__ == "__main__":
    main()
