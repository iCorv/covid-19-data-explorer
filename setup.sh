mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"corvin.jaedicke@cjaedicke.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[client]\n\
caching = true\n\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml