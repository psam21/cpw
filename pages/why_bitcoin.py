"""
Why Bitcoin page content.
"""
import streamlit as st
from utils.debug_logger import debug_log_user_action


def render_why_bitcoin_page():
    """Render the Why Bitcoin page"""
    debug_log_user_action("Viewing Why Bitcoin page")
    
    st.header("Why Bitcoin is the Most Powerful Store of Value")
    
    # Compact two-column layout
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌟 Key Characteristics")
        
        st.markdown("""
        **🔒 Decentralization**  
        Bitcoin operates on a peer-to-peer network, free from control by any single entity, making it resistant to censorship and manipulation.
        
        **💎 Limited Supply**  
        Only 21 million bitcoins will ever exist, protecting against inflationary pressures that plague fiat currencies.
        
        **🛡️ Security**  
        Secured by massive computing power through proof-of-work, making it incredibly difficult to alter transaction history.
        
        **🌍 Portability & Divisibility**  
        Can be sent globally with internet access and divided into smaller units for accessibility.
        """)
    
    with col_right:
        st.subheader("⚡ Bitcoin's Legacy")
        
        st.markdown("""
        **🏛️ Digital Gold**  
        Bitcoin has emerged as a revolutionary store of value, often called "digital gold" due to its scarcity and store-of-value properties.
        
        **🚀 Resistance Money**  
        As the world faces economic uncertainty and currency devaluation, Bitcoin stands as a beacon of financial sovereignty.
        
        **🔮 Future of Finance**  
        Bitcoin represents money truly owned by the people, resistant to the whims of central planners and government manipulation.
        
        **📈 Unstoppable Growth**  
        Its journey has just begun, with unlimited potential to reshape the global financial system.
        """)
    
    # Compact conclusion
    st.subheader("🎯 The Bottom Line")
    st.info("""
    Bitcoin is more than just a cryptocurrency—it's a paradigm shift towards decentralized, sound money. 
    Its unique combination of scarcity, security, and decentralization makes it the most powerful store of value in human history.
    """)
