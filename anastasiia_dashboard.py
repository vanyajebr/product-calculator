import streamlit as st
import pandas as pd
import locale

# Set German number format
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

def euro_format(value):
    return locale.currency(value, grouping=True)

def calculate_heizlastberechnung(area_m2, apply_discount=True):
    """Calculate Heizlastberechnung price with optional 20% discount"""
    if area_m2 <= 150:
        original_price = 900
    elif area_m2 <= 250:
        original_price = 1250
    else:
        original_price = 1000 + (4 * (area_m2 - 250))
    
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

def main():
    st.title("🧮 Product Bundle Calculator")
    st.markdown("---")
    
    st.header("📋 Input Information")
    
    col1, col2 = st.columns(2)
    with col1:
        wohneinheiten = st.number_input("Number of Wohneinheiten", min_value=1, value=1, step=1)
    with col2:
        area_m2 = st.number_input("Area (m²)", min_value=1, value=100, step=1)
    
    if 'include_isfp' not in st.session_state:
        st.session_state.include_isfp = True
    
    include_isfp = st.checkbox("Include iSFP", value=st.session_state.include_isfp)
    st.session_state.include_isfp = include_isfp
    
    st.markdown("---")
    
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
        
        heiz_forderung = heiz_discounted * 0.5
        heiz_final = heiz_discounted - heiz_forderung
        
        hydr_forderung = hydr_discounted * 0.5
        hydr_final = hydr_discounted - hydr_forderung
        
        if include_isfp:
            total_discounts = (heiz_original - heiz_discounted) + (hydr_original - hydr_discounted)
            total_forderung = heiz_forderung + hydr_forderung + isfp_subsidy
            total_full_price = heiz_discounted + hydr_discounted + isfp_original
            total_user_pays = heiz_final + hydr_final + isfp_final
        else:
            total_discounts = (heiz_original - heiz_discounted) + (hydr_original - hydr_discounted)
            total_forderung = heiz_forderung + hydr_forderung
            total_full_price = heiz_discounted + hydr_discounted
            total_user_pays = heiz_final + hydr_final
        
        # Investment cost limit (using full prices)
        investment_cost_limit = (30000 * wohneinheiten) - (heiz_original + hydr_original + (900 * wohneinheiten))
        
        # Results section
        st.header(f"📊 Calculation Results - {bundle_type}")
        col1, col2, col3 = st.columns(3)
        with col1:
            discount_text = f"-{euro_format(total_discounts)} (20% discount)" if total_discounts > 0 else "No discount"
            st.metric("Full Price", euro_format(total_full_price), delta=discount_text)
        with col2:
            st.metric("User Pays", euro_format(total_user_pays))
        with col3:
            st.metric("Forderung Subsidy", euro_format(total_forderung))
        
        # Breakdown table
        st.subheader("📋 Detailed Breakdown")
        breakdown_data = [
            {
                'Product': 'Heizlastberechnung',
                'Original Price': euro_format(heiz_original),
                'After 20% Discount': euro_format(heiz_discounted),
                'Forderung': euro_format(heiz_forderung),
                'Final Price': euro_format(heiz_final)
            },
            {
                'Product': 'Hydraulischer Abgleich',
                'Original Price': euro_format(hydr_original),
                'After 20% Discount': euro_format(hydr_discounted),
                'Forderung': euro_format(hydr_forderung),
                'Final Price': euro_format(hydr_final)
            }
        ]
        if include_isfp:
            breakdown_data.append({
                'Product': 'iSFP',
                'Original Price': euro_format(isfp_original),
                'After 20% Discount': euro_format(isfp_original),
                'Forderung': euro_format(isfp_subsidy),
                'Final Price': euro_format(isfp_final)
            })
        df = pd.DataFrame(breakdown_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Bottom explanation text
        st.markdown("---")
        st.subheader("📄 Dies ist ein Template, das Sie in die Vorlage EffizienzBegleitung HH+ einfügen sollen.")
        st.markdown(
            f"Für Ihr **{wohneinheiten}** WE-Haus mit **{area_m2} m²** beträgt der Preis für die Energie-Begleitung "
            f"**{euro_format(total_full_price)}** (Vollpreis) sowie zusätzlich 3 % für die Einzelmaßnahme Heizung.\n\n"
            f"Es gibt eine 50 % Förderung auf unsere Leistungen in Höhe von **{euro_format(total_forderung)}** "
            f"sowie zusätzlich eine 1,5 % Förderung für die Einzelmaßnahme Heizung = "
            f"**{euro_format(total_user_pays)}** + 1,5 % Endpreis.\n\n"
            f"Falls das Angebot für Heizung und Montage in Ihrem Fall mehr als **{euro_format(investment_cost_limit)}** "
            f"beträgt, überschreitet dies die durch die KfW festgelegten staatlichen Fördergrenzen für unsere Leistungen. "
            f"In diesem Fall entfällt die Förderung für diesen Teil unserer Arbeit, und Sie zahlen den vollen Preis für dieses Produkt."
        )

if __name__ == "__main__":
    main()
