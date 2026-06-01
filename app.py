import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# એપનું પેજ સેટઅપ
st.set_page_config(page_title="Shree Hari Dairy Farm", page_icon="🥛", layout="wide")

# કંપની પ્રોફાઈલ વિગતો
OWNER_NAME = "Hardeepsinh Jadeja"
PHONE_NUMBER = "+91 XXXXXXXXXX"

# મોક ડેટાબેઝ (શરૂઆત માટે ગ્રાહકોનું લિસ્ટ સેટ કર્યું છે)
if 'customers' not in st.session_state:
    st.session_state.customers = [
        {"id": 1, "name": "ધર્મેન્દ્રસિંહ મધુવન", "morning_default": 33.5, "evening_default": 0, "balance": 0},
        {"id": 2, "name": "મહાવીરસિંહ ગાયત્રી", "morning_default": 47.0, "evening_default": 0, "balance": 0},
        {"id": 3, "name": "દેવયાની દીદી", "morning_default": 60.0, "evening_default": 0, "balance": 0},
        {"id": 4, "name": "હરપาลસિંહ", "morning_default": 0, "evening_default": 53.5, "balance": 0},
        {"id": 5, "name": "ભાણાભાઈ", "morning_default": 0, "evening_default": 19.0, "balance": 0}
    ]

if 'milk_records' not in st.session_state:
    st.session_state.milk_records = {}

if 'cattle_notes' not in st.session_state:
    st.session_state.cattle_notes = []

# વર્તમાન સમય અને ટંક (Shift) ઓટો-ડિટેક્ટ
current_time = datetime.now()
current_date_str = current_time.strftime("%Y-%m-%d")
current_hour = current_time.hour
default_shift = "સવાર" if current_hour < 15 else "સાંજ"

# --- હેડર અને ડેશબોર્ડ ---
st.title("🥛 શ્રી હરિ ડેરી ફાર્મ - સુરેન્દ્રનગર")
st.subheader(f"પ્રોપ્રાયટર: {OWNER_NAME} | મો. {PHONE_NUMBER}")
st.markdown("---")

# ડેશબોર્ડ કાઉન્ટર્સ (આજનું અને ગઈકાલનું દૂધ)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="📅 આજની તારીખ", value=current_time.strftime("%d-%m-%Y"))
with col2:
    st.metric(label="☀️ આજનું સવારનું કુલ દૂધ", value="883 Ltr")
with col3:
    st.metric(label="🌙 આજનું સાંજનું કુલ દૂધ", value="741 Ltr")
with col4:
    st.metric(label="🏆 આખરી કુલ દૂધ (મે)", value="1,624 Ltr")

# --- મુખ્ય વિભાગો (Tabs) ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 દૂધ એન્ટ્રી (રોજિંદી)", "👥 ગ્રાહક મેનેજમેન્ટ", "🐄 ગાયોની પ્રેગ્નન્સી નોટ્સ", "📄 માસિક બિલ અને PDF"])

# --- TAB 1: રોજિંદી દૂધ એન્ટ્રી (તમારી મુખ્ય શરત મુજબ) ---
with tab1:
    st.header("📝 રોજિંદી સ્માર્ટ એન્ટ્રી")
    
    col_date, col_shift = st.columns(2)
    with col_date:
        selected_date = st.date_input("તારીખ પસંદ કરો", current_time)
    with col_shift:
        selected_shift = st.selectbox("ટંક પસંદ કરો", ["સવાર", "સાંજ"], index=0 if default_shift == "સવાર" else 1)
        
    st.info(f"💡 તમે **{selected_shift}** નો સેક્શન ખોલ્યો છે. નીચે ગ્રાહકો તેમના ફિક્સ દૂધના ક્રમમાં ગોઠવાયેલા છે.")
    
    # એન્ટ્રી ફોર્મ
    date_key = f"{selected_date}_{selected_shift}"
    if date_key not in st.session_state.milk_records:
        st.session_state.milk_records[date_key] = {}
        
    entries = {}
    
    # ગ્રાહકોનું લિસ્ટ ફિલ્ટર કરીને બતાવવું
    for cust in st.session_state.customers:
        default_qty = cust["morning_default"] if selected_shift == "સવાર" else cust["evening_default"]
        
        # જો ગ્રાહક એ ટંકમાં દૂધ લેતો હોય તો જ બતાવે
        if default_qty > 0:
            col_name, col_qty = st.columns([3, 1])
            with col_name:
                st.write(f"🔹 **{cust['name']}** (નિયમિત દૂધ: {default_qty} Ltr)")
            with col_qty:
                # અહીં દૂધની માત્રા ઓછી-વધુ કરી શકાય
                entries[cust["id"]] = st.number_input(f"લીટર ({cust['name']})", min_value=0.0, value=float(default_qty), step=0.5, label_visibility="collapsed")

    # સિંગલ ક્લિક જથ્થાબંધ એન્ટ્રી બટન
    if st.button(f"🚀 એક ક્લિકમાં {selected_shift}ના બધા જ દૂધની એન્ટ્રી સેવ કરો", type="primary"):
        st.session_state.milk_records[date_key] = entries
        st.success(f"🎉 {selected_date} - {selected_shift}નો હિસાબ સફળતાપૂર્વક લોક થઈ ગયો છે!")

# --- TAB 2: ગ્રાહકોનો વિભાગ (માત્રા સેટ કરવી / બાકી રૂપિયા) ---
with tab2:
    st.header("👥 ગ્રાહકોની માસ્ટર પ્રોફાઈલ")
    
    # નવો ગ્રાહક ઉમેરવો
    with st.expander("➕ નવો ગ્રાહક ઉમેરો"):
        new_name = st.text_input("ગ્રાહકનું નામ")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            m_def = st.number_input("સવારનું ફિક્સ દૂધ (લીટર)", min_value=0.0, value=0.0)
        with c_col2:
            e_def = st.number_input("સાંજનું ફિક્સ દૂધ (લીટર)", min_value=0.0, value=0.0)
        init_bal = st.number_input("શરૂઆતની બાકી રકમ (રૂપિયા)", value=0)
        
        if st.button("ગ્રાહક સેવ કરો"):
            new_id = len(st.session_state.customers) + 1
            st.session_state.customers.append({
                "id": new_id, "name": new_name, "morning_default": m_def, "evening_default": e_def, "balance": init_bal
            })
            st.success("ગ્રાહક ઉમેરાઈ ગયો!")

    # ગ્રાહકોનું લિસ્ટ ટેબલ સ્વરૂપે
    st.subheader("📋 હાલના ગ્રાહકો અને તેમનું ફિક્સ દૂધ")
    df_cust = pd.DataFrame(st.session_state.customers)
    df_cust.columns = ["ID", "ગ્રાહકનું નામ", "સવારનું ફિક્સ (L)", "સાંજનું ફિક્સ (L)", "બાકી/જમા રકમ (₹)"]
    st.dataframe(df_cust, use_container_width=True)

# --- TAB 3: ગાયોની પ્રેગ્નન્સી અને ડિલિવરી નોટ્સ ---
with tab3:
    st.header("🐄 પશુપાલન અને ગાયોનું રેકોર્ડ ટ્રેકિંગ")
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        cow_tag = st.text_input("ગાયનું નામ અથવા ટેગ નં.", placeholder="દા.ત. ગંગા, કાબરી, 101")
    with col_c2:
        preg_date = st.date_input("પ્રેગ્નન્સી (AI / સંવર્ધન) તારીખ")
    with col_c3:
        # ઓટોમેટિક ડિલિવરી તારીખ ગણવી (ગાયનો ગર્ભકાળ આશરે ૨૮૩ દિવસ)
        est_delivery = preg_date + timedelta(days=283)
        st.write("📅 **સંભવિત ડિલિવરી તારીખ:**")
        st.info(est_delivery.strftime("%d-%m-%Y"))
        
    additional_note = st.text_area("અન્ય કોઈ ખાસ નોંધ (રસીકરણ, દવા વગેરે)")
    
    if st.button("📌 ગાયની વિગત નોટબુકમાં સેવ કરો"):
        st.session_state.cattle_notes.append({
            "cow": cow_tag, "preg": preg_date.strftime("%d-%m-%Y"), "delivery": est_delivery.strftime("%d-%m-%Y"), "note": additional_note
        })
        st.success("નોંધ સાચવી લેવામાં આવી છે!")
        
    # સેવ કરેલી નોટ્સ બતાવવી
    if st.session_state.cattle_notes:
        st.subheader("📋 ફાર્મની સક્રિય નોંધપોથી")
        st.table(pd.DataFrame(st.session_state.cattle_notes))

# --- TAB 4: ઓટોમેટિક બિલ, પીડીએફ અને વોટ્સએપ શેર ---
with tab4:
    st.header("📄 બિલિંગ સેન્ટર")
    
    selected_cust_id = st.selectbox("બિલ માટે ગ્રાહક પસંદ કરો", [c["id"] for c in st.session_state.customers], format_func=lambda x: [c["name"] for c in st.session_state.customers if c["id"]==x][0])
    bill_month = st.selectbox("મહિનો પસંદ કરો", ["મે - 2026", "જૂન - 2026"])
    
    bill_note = st.text_input("બિલ નીચે ખાસ નોંધ લખો", value="દૂધ હંમેશા ઉકાળીને વાપરવું. શ્રી હરિ ડેરી ફાર્મ પસંદ કરવા બદલ આભાર!")
    
    # ટેમ્પરરી બિલ પ્રીવ્યૂ
    st.markdown("---")
    st.markdown(f"### 📄 **શ્રી હરિ ડેરી ફાર્મ - મોકલવા પાત્ર બિલ પ્રીવ્યૂ**")
    st.write(f"**ગ્રાહક:** {[c['name'] for c in st.session_state.customers if c['id']==selected_cust_id][0]}")
    st.write(f"**મહિનો:** {bill_month}")
    
    # મોક બિલ સરવાળો
    total_l = 47.0
    total_r = 2820
    bal_r = 0
    
    st.markdown(f"""
    | વિગત | જથ્થો / રકમ |
    | :--- | :---: |
    | **કુલ સવાર+સાંજ દૂધ** | {total_l} લીટર |
    | **ચાલુ મહિનાની રકમ** | {total_r}/- ₹ |
    | **આગળના બાકી/જમા રૂપિયા** | {bal_r}/- ₹ |
    | **🏆 કુલ ચૂકવવાપાત્ર રકમ** | **{total_r + bal_r}/- રૂપિયા** |
    """)
    st.caption(f"📝 *નોંધ: {bill_note}*")
    
    # વોટ્સએપ શેરિંગ લિંક જનરેટ કરવી
    cust_name = [c['name'] for c in st.session_state.customers if c['id']==selected_cust_id][0]
    whatsapp_msg = f"જય મુરલીધર! 🙏 *શ્રી હરિ ડેરી ફાર્મ* તરફથી {bill_month} માસનું બિલ.\n\nગ્રાહક: {cust_name}\nકુલ દૂધ: {total_l} લીટર\nકુલ રકમ: {total_r}/- ₹\n\nનોંધ: {bill_note}"
    encoded_msg = whatsapp_msg.replace("\n", "%0A").replace(" ", "%20")
    whatsapp_url = f"https://wa.me/?text={encoded_msg}"
    
    col_pdf, col_wa = st.columns(2)
    with col_pdf:
        if st.button("📥 ઓટોમેટિક PDF ડાઉનલોડ કરો", type="secondary"):
            st.info("PDF જનરેટ થઈ રહી છે... (તમારા પ્રિન્ટ ફોર્મેટ મુજબ)")
    with col_wa:
        st.markdown(f' <a href="{whatsapp_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">📲 સીધું WhatsApp પર શેર કરો</button></a>', unsafe_allow_html=True)
