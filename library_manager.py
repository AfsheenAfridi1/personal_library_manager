import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Personal Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>      
.main-header { 
    font-size: 3rem !important;
    color: #1E3A8A;
    font-weight: 700;
    margin-bottom: 1rem;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.sub_header {
    font-size: 1.8rem !important;
    color: #3B82F6;
    font-weight: 600;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.success-message {
    padding: 1rem;
    background-color: #ECFDF5;
    border-left: 5px solid #10B981;
    border-radius: 0.375rem;    
}            
.warning-message {
    padding: 1rem;
    background-color: #FEF3C7;
    border-left: 5px solid #F59E0B;
    border-radius: 0.375rem;   
}
.book-card {
    background-color: #F3F4F6;
    border-radius: 0.5rem;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 5px solid #3B82F6;           
    transition: transform 0.3s ease;
}
.book-card-hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); 
}
.read-badge {
    background-color: #10B981;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 600;    
}
.unread-badge {
    background-color: #F87171;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 600;    
}
.action-button {
    margin-right: 0.5rem;
}
.stButton > button {
    border-radius: 0.375rem;
}
</style>            
""", unsafe_allow_html=True)

# Load Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None 
        return r.json()
    except:
        return None

# Initialize session state
if "library" not in st.session_state:
    st.session_state.library = []
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "book_added" not in st.session_state:
    st.session_state.book_added = False
if "book_removed" not in st.session_state:
    st.session_state.book_removed = False
if "current_view" not in st.session_state:
    st.session_state.current_view = "library"

# Load library
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.library = json.load(file)
                return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# Save library
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a book to library
def add_book(title, author, publication_year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# Remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search books
def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

# Calculate library stats
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book["read_status"])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decade_counts = {}

    for book in st.session_state.library:
        # Genre count
        genres[book["genre"]] = genres.get(book["genre"], 0) + 1
        # Author count
        authors[book["author"]] = authors.get(book["author"], 0) + 1
        # Decade count
        decade = (int(book["publication_year"]) // 10) * 10
        decade_counts[decade] = decade_counts.get(decade, 0) + 1

    # Sort data
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decade_counts = dict(sorted(decade_counts.items(), key=lambda x: x[0]))

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percent_read": percent_read,
        "genres": genres,
        "authors": authors,
        "decades": decade_counts
    }

def create_visulations(stats):
    if stats["total_books"] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels= ["Read" , "Unread"],
            values=[stats["read_books"],stats["total_books"],stats["percentage_read"]- stats["read_books"]],
            hole=.4,
            marker_colors=["#10B981" , "#F87171"]
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status,use_container_width=True)

        # Bar chart genres
        if stats["genres"]:
            genres_df = pd.DataFrame({
                "Genre": list(stats["genres"].keys()),
                "Count": list(stats["genres"].values())
            })
            fig_genres = px.bar(
                genres_df,
                x="Genre",
                y="Count",
                color="Count",
                color_continous_scale=px.colors.sequential.Blues
            )
            fig_genres.update_layout(
                title_text="Books by Publication Genre",
                xaxis_title="Genres",
                yaxis_title="Number of Books",
                height=400
            )
            st.plotly_chart(fig_genres,use_container_width=True)

            # Line chart decades
            if stats["decades"]:
                decades_df = pd.DataFrame({
                    "Decade": [f"{decade}s" for decade in stats["decades"].keys()],
                    "Count": list(stats["decades"].values())
                })
                fig_decades = px.line(
                   decades_df,
                   x="Decade",
                   y="Count",
                   markers=True,
                   line_shape="spline"
                )
                fig_decades.update_layout(
                   title_text="Books by Publication Decade",
                   xaxis_title="Decade",
                   yaxis_title="Number of Books",
                   height=400
                )
                st.plotly_chart(fig_decades, use_container_width=True)

# Load library
load_library()

# Sidebar for navigation
st.sidebar.markdown("<h1 style='text-align: center;'> Navigation</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets9.lottieflies.com/temp/1f20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key="book_animation")

nav_options = st.sidebar.radio("Choose an option:", ["View Library", "Add Book", "Search Books", "Library Statistics"])

if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"
    

st.markdown("<h1 class='main-header'> Personal Library Manager </h1>", unsafe_allow_html=True)

if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'> Add a New Book</h2>", unsafe_allow_html=True)

    # Adding books input form
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)

        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-fiction", "Fantasy", "Science Fiction", "Biography", 
                "History", "Mystery", "Other"
            ])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        
        submit_button = st.form_submit_button(label="Add Book")

    if submit_button and title and author:
        add_book(title, author, publication_year, genre, read_bool)

        if st.session_state.book_added:
            st.markdown("<div class='success-message'> Book added successfully!</div>", unsafe_allow_html=True)
            st.balloons()
            st.session_state



    read_status = st.radio ("Read Status",["Read","Unread"],horizontal=True)


    if st.session_state.book_added:
     st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
    st.balloons()
    st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>Your Library</h2>", unsafe_allow_html=True)

    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your Library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                    <div class='book-card'>
                        <h3>{book['title']}</h3>
                        <p><strong>Author:</strong> {book['author']}</p>
                        <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                        <p><strong>Genre:</strong> {book['genre']}</p>
                        <p><span class='{ "read-badge" if book["read_status"] else "unread-badge"}'>
                            {'Read' if book["read_status"] else 'Unread'}
                        </span></p>
                    </div>
                """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove", key=f"remove_{i}", use_container_width=True):
                    if remove_book(i):
                        st.rerun()
            with col2:
                new_status = not book['read_status']
                status_label = "Mark as read" if not book['read_status'] else "Mark as unread"
                if st.button(status_label, key=f"status_{i}", use_container_width=True):
                    st.session_state.library[i]["read_status"] = new_status
                    save_library()
                    st.rerun()

if st.session_state.book_removed:
    st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)
    st.session_state.book_removed = False

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>Search Books</h2>", unsafe_allow_html=True)

    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter search term:")

    if st.button("Search", use_container_width=False):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_books(search_term, search_by)
        if hasattr(st.session_state, "search_results"):
            if st.session_state.search_results:
                st.markdown(f"<h3>Found {len(st.session_state.search_results)} results:</h3>", unsafe_allow_html=True)
                for i, book in enumerate(st.session_state.search_results):
                    st.markdown(f"""
                        <div class='book-card'>
                            <h3>{book['title']}</h3>
                            <p><strong>Author:</strong> {book['author']}</p>
                            <p><strong>Publication Year:</strong> {book['publication_year']}</p>
                            <p><strong>Genre:</strong> {book['genre']}</p>
                            <p><span class='{ "read-badge" if book["read_status"] else "unread-badge"}'>
                                {'Read' if book["read_status"] else 'Unread'}
                            </span></p>
                        </div>
                    """, unsafe_allow_html=True)
            elif search_term:
                st.markdown("<div class='warning-message'>No books found matching your search.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>Library Statistics</h2>", unsafe_allow_html=True)
  
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your Library is empty. Add some books to see stats!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Books", stats['total_books'])
        with col2:
            st.metric("Books Read", stats['read_books'])
        with col3:
           st.metric("Percent Read %",f" {stats['percent_read']}%")
    
    def create_visualizations(stats):
    # Example: Use matplotlib or Streamlit charts
               st.subheader(" Books Read  Total Books")
    st.bar_chart({
           'Book': ['Books Read', 'Total Books', 'Read %'],
        'Count': [stats['read_books'], stats['total_books'], stats['percent_read']]
})

st.markdown("---")
st.markdown("Copyright @ 2025 Afsheen Afridi Personal Library Manager", unsafe_allow_html=True)
