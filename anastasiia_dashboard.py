import streamlit as st
import pandas as pd

# --- Safe German currency formatting without system locales ---
def euro_de(value: float) -> str:
    # Format like 1,234.56 then swap separators to 1.234,56 and append €
    s = f"{value:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"

def calculate_heizlastberechnung(area_m2, apply_discount=True):
    """Calculate Heizlastberechnung price with optional 20% discount"""
    if area_m2 <= 150:
        original_price = 900
    elif area_m2 <= 250:
        original_price = 1250
    else:
        original_price = 1250 + (4 * (area_m2 - 250))
    discounted_price = original_price * 0.8 if apply_discount else original_price
    return original_price, discounted_price

def calculate_hydraulischer_abgleich(area_m2, apply_discount=False):
    """Calculate Hydraulischer Abgleich with optional 20% discount"""
    if area_m2 <= 150:
        original_price = 800
    elif area_m2 <= 250:
        original_price = 900
    else:
        original_price = 900 + (4 * (area_m2 - 250))
    discounted_price = original_price * 0.8 if apply_discount else original_price
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

# --- Base investment cap by WE:
# 1 WE = 30k; +15k per WE up to 6 WE (→ 105k);
# from 7 WE onward = +8k per WE (7 WE = 113k, 8 WE = 121k, ...).
def investment_base_cap(wohneinheiten: int) -> int:
    if wohneinheiten <= 1:
        return 30000
    elif wohneinheiten <= 6:
        return 30000 + 15000 * (wohneinheiten - 1)
    else:
        # 6 WE is 105k; add 8k for each WE above 6
        return 105000 + 8000 * (wohneinheiten - 6)

def main():
    st.title("🧮 Energieberatungs-Begleitung Heizung+ Calculator")
    st.markdown("---")
    
    # Inputs
    st.header("📋 Input Information")
    col1, col2 = st.columns(2)
    with col1:
        wohneinheiten = st.number_input("Number of Wohneinheiten", min_value=1, value=1, step=1)
    with col2:
        area_m2 = st.number_input("Area (m²)", min_value=1, value=100, step=1)
    
    # Checkbox state
    if 'include_isfp' not in st.session_state:
        st.session_state.include_isfp = True
    include_isfp = st.checkbox("Include iSFP", value=st.session_state.include_isfp)
    st.session_state.include_isfp = include_isfp
    
    st.markdown("---")
    
    # Calculate
    if st.button("💰 Calculate Total Price", type="primary"):
        # Bundle logic
        if include_isfp:
            heiz_original, heiz_discounted = calculate_heizlastberechnung(area_m2, True)
            hydr_original, hydr_discounted = calculate_hydraulischer_abgleich(area_m2, False)
            isfp_original, isfp_final, isfp_subsidy = calculate_isfp(wohneinheiten)
            bundle_type = "Full Bundle (with iSFP)"
        else:
            heiz_original, heiz_discounted = calculate_heizlastberechnung(area_m2, False)
            hydr_original, hydr_discounted = calculate_hydraulischer_abgleich(area_m2, True)
            isfp_original, isfp_final, isfp_subsidy = 0, 0, 0
            bundle_type = "2 Products Bundle (without iSFP)"
        
        # Subsidies & finals
        heiz_forderung = heiz_discounted * 0.5
        heiz_final = heiz_discounted - heiz_forderung
        
        hydr_forderung = hydr_discounted * 0.5
        hydr_final = hydr_discounted - hydr_forderung
        
        # Totals (match your existing "Calculation Results")
        total_discounts = (heiz_original - heiz_discounted) + (hydr_original - hydr_discounted)
        if include_isfp:
            total_forderung = heiz_forderung + hydr_forderung + isfp_subsidy
            total_full_price = heiz_discounted + hydr_discounted + isfp_original
            total_user_pays = heiz_final + hydr_final + isfp_final
        else:
            total_forderung = heiz_forderung + hydr_forderung
            total_full_price = heiz_discounted + hydr_discounted
            total_user_pays = heiz_final + hydr_final
        
        # --- Investment cost limit ---
        # Base cap per WE schedule, then subtract HB/HA full prices and 900 € per WE
        base_cap = investment_base_cap(int(wohneinheiten))
        investment_cost_limit = base_cap - (heiz_original + hydr_original + (900 * wohneinheiten))
        
        # Results header
        st.header(f"📊 Calculation Results - {bundle_type}")
        c1, c2, c3 = st.columns(3)
        with c1:
            if total_discounts > 0:
                delta_text = f"-{euro_de(total_discounts)} (20 % Rabatt)"
            else:
                delta_text = "Kein Rabatt"
            st.metric("Full Price", euro_de(total_full_price), delta=delta_text)
        with c2:
            st.metric("User Pays", euro_de(total_user_pays))
        with c3:
            st.metric("Forderung Subsidy", euro_de(total_forderung))
        
        # Breakdown
        st.subheader("📋 Detailed Breakdown")
        breakdown_data = [
            {
                'Product': 'Heizlastberechnung',
                'Original Price': euro_de(heiz_original),
                'After 20% Discount': euro_de(heiz_discounted),
                'Forderung': euro_de(heiz_forderung),
                'Final Price': euro_de(heiz_final)
            },
            {
                'Product': 'Hydraulischer Abgleich',
                'Original Price': euro_de(hydr_original),
                'After 20% Discount': euro_de(hydr_discounted),
                'Forderung': euro_de(hydr_forderung),
                'Final Price': euro_de(hydr_final)
            }
        ]
        if include_isfp:
            breakdown_data.append({
                'Product': 'iSFP',
                'Original Price': euro_de(isfp_original),
                'After 20% Discount': euro_de(isfp_original),  # no discount on iSFP in your logic
                'Forderung': euro_de(isfp_subsidy),
                'Final Price': euro_de(isfp_final)
            })
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Bottom explanatory text (uses values exactly from results)
        st.markdown("---")
        st.subheader("📄 Dies ist ein Template, das Sie in die Vorlage Energieberatungs-Begleitung Heizung+ einfügen sollen.")
        st.markdown(
            f"""
            <p style="font-family: Arial; font-size:14.5px; color:black; font-weight: bold; background-color:transparent;">
            Für Ihr {wohneinheiten} WE-Haus mit {area_m2} m² beträgt der Preis für die Energie-Begleitung 
            {euro_de(total_full_price)} (Vollpreis) sowie zusätzlich 3 % für die Einzelmaßnahme Heizung.<br><br>
            Es gibt eine 50 % Förderung auf unsere Leistungen in Höhe von {euro_de(total_forderung)} 
            sowie zusätzlich eine 1,5 % Förderung für die Einzelmaßnahme Heizung = 
            <span style="font-weight:bold; font-size: 18px;">{euro_de(total_user_pays)} + 1,5 % Endpreis</span>.<br><br>
            Falls das Angebot für Heizung und Montage in Ihrem Fall mehr als {euro_de(investment_cost_limit)} 
            beträgt, überschreitet dies die durch die KfW festgelegten staatlichen Fördergrenzen für unsere Leistungen. 
            In diesem Fall entfällt die Förderung für diesen Teil unserer Arbeit, und Sie zahlen den vollen Preis für dieses Produkt.
            </p>
            """,
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
