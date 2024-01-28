import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def get_link(movie_or_tvshow):
    url = f"https://www.justwatch.com/in/{movie_or_tvshow}?release_year_from=2022&rating_imdb=7"
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        link_list = soup.find("div", class_="title-list-grid")
        links = link_list.find_all("div", class_="title-list-grid__item")
        urls_list = []
        count = 0
        for link in links:
            item_url = link.find("a", class_="title-list-grid__item--link")["href"]
            urls_list.append(item_url)
            count += 1
            if count == 5:  # <--- Number of movies or tvshow data scraped
                break
        return urls_list
    else:
        print(f"Failed to get data from {url} ; Status Code : {response.status_code}")
        return []


def get_data(url):
    url = f"https://www.justwatch.com{url}"
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, "lxml")

        try:
            title = soup.find("h1").text
        except:
            title = None

        try:
            year = soup.find("span", class_="text-muted").text.strip()[1:-1]
        except:
            year = None

        try:
            genres = soup.find("h3", string="Genres").find_next("div").text
        except:
            genres=None

        try:
            rating_imdb = (
                soup.find_all("div", class_="jw-scoring-listing__rating")[1]
                .div.span.span.text.strip()
                .split()[0]
           )
        except:
            rating_imdb = None

        try:
            streaming = soup.find("p", attrs={"data-v-3f103c69": True}).text.partition(
                " on "
            )[2]
        except:
            streaming = None

        data_dict = {
            "Title": title,
            "Year": year,
            "Genres": genres,
            "Imdb": float(rating_imdb),
            "Streaming": streaming,
            "URL": url,
        }

        if "movie" in url:
            movie_list.append(data_dict)
        else:
            tvshow_list.append(data_dict)

    else:
        print(
            f"Failed to recieve data from {url} ; Status Code : {response.status_code}"
        )


def create_excel():
    movie_dataframe = pd.DataFrame(movie_list)
    movie_dataframe.index += 1

    tvshow_dataframe = pd.DataFrame(tvshow_list)
    tvshow_dataframe.index += 1

    try:
        movie_dataframe.to_csv("Movies.csv")
        print("Movies Csv Saved!")
    except Exception as e:
        print(f"Failed to save csv : {e}")

    try:
        tvshow_dataframe.to_csv("TvShows.csv")
        print("TvShows Csv Saved!")
    except Exception as e:
        print(f"Failed to save csv : {e}")

    timer = round(time.time() - start_time, 2)
    timer = time.strftime("%M:%S", time.gmtime(timer))
    print(f"The process has been completed.\nTime Taken :{timer}")

    print(f'Average Movie Imbd : {movie_dataframe['Imdb'].mean(numeric_only=True,skipna=True)}')
    print(f'Average TvShow Imbd : {tvshow_dataframe['Imdb'].mean(numeric_only=True,skipna=True)}')


print("Collecting Data...Please Wait...")
start_time = time.time()
movie_list = []
tvshow_list = []
tvshow = "tv-shows"
movie = "movies"

urls_list = get_link(movie)
for movie_url in urls_list:
    get_data(movie_url)

urls_list = get_link(tvshow)
for tvshow_url in urls_list:
    get_data(tvshow_url)


create_excel()
