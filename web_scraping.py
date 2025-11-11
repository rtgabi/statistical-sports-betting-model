from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import date

def get_team_goals(team_name: str, opponent: str, start_year: int) -> ({}, {}):
    """
    :param team_name: Name of the wanted team to look for (exactly as it can be found on "Flashscore")
    :param opponent: Name of the wanted team's opponent (exactly as it can be found on "Flashscore")
    :param start_year: The year the games should be started from (e.g. 2020)
    :return: Tuple of 2 dictionaries: 1. "goals scored", 2. "head_to_head"
    """

    # Setup the driver to open on "Flashscore"
    driver=webdriver.Chrome()
    driver.maximize_window()
    base_url='https://www.flashscore.com/'

    # "goals" -> list which contains all the goals a team scored in the selected period
    # "results" -> list of "Win"/"Lose"/"Draw" for every game played by the team in the selected period
    # "home" -> list of goals scored by the team in Home games
    # "away" -> list of goals scored by the team in Away games
    goals_scored={
        'goals': [],
        'results': [],
        'home': [],
        'away': []
    }

    try:
        driver.get(base_url)

        # Reject cookies when they show up
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-reject-all-handler'))
            ).click()
        except:
            pass

        # Click the search window
        search_box=WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.ID, 'search-window'))
        )
        search_box.click()

        # Type the team's name into the search box.
        search_input=WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'searchInput__input'))
        )
        search_input.send_keys(team_name)

        time.sleep(3)

        # Click on the searched team
        team_link=WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "searchResult"))
        )
        team_link.click()

        # Go to the "Results" tab
        results_tab=WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Results']"))
        )
        results_tab.click()

        current_year = date.today().year
        # Number of times to press the "Show more matches" button
        years_to_scrape=range(start_year, current_year+1)
        actions=ActionChains(driver)

        for year in reversed(years_to_scrape):
            try:
                time.sleep(1)

                # Click the "Show more matches" button
                show_more_button=WebDriverWait(driver,10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[text()='Show more matches']"))
                )
                actions.move_to_element(show_more_button).click()
                show_more_button.click()
                time.sleep(3)
            except:
                print(f'No more matches to load for {year} or button not found.')

        # Stores the "WebDriverWait" object returned
        match_elements=WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.event__match'))
        )

        # Get the "Head to head" results of a team and its opponent
        head_to_head={
            f'{team_name}': [],
            f'{opponent}': []
        }

        # Stores the "text" of each object from "match_elements", split by ","
        res=[match_elements[i].text.split('\n') for i in range(len(match_elements))]
        for i in range(len(res)):

            try:
                if int(res[i][0][-4:])<start_year:
                    break
            except ValueError:
                pass

            try:
                # If the first element is the searched team's name
                if res[i][1]==team_name:
                    # Store the third element (the first team's amount of goals)
                    goals=int(res[i][3])
                    # Add the object in the "goals" and "home" lists
                    goals_scored['goals'].append(goals)
                    goals_scored['home'].append(goals)

                    # Check the result of the game
                    if res[i][-1]=='W':
                        goals_scored['results'].append('Win')
                    elif res[i][-1]=='L':
                        goals_scored['results'].append('Loss')
                    elif res[i][-1]=='D':
                        goals_scored['results'].append('Draw')

                    # Check if the team played against is the team we want the h2h results
                    if res[i][2]==opponent:
                        head_to_head[f'{team_name}'].append(goals)
                        head_to_head[f'{opponent}'].append(int(res[i][4]))

                # If the second element is the searched team's name
                elif res[i][2]==team_name:
                    # Store the fourth element (the second team's amount of goals)
                    goals=int(res[i][4])
                    # Add the object in the "goals" and "away" lists this time
                    goals_scored['goals'].append(goals)
                    goals_scored['away'].append(goals)

                    if res[i][-1]=='W':
                        goals_scored['results'].append('Win')
                    elif res[i][-1]=='L':
                        goals_scored['results'].append('Loss')
                    elif res[i][-1]=='D':
                        goals_scored['results'].append('Draw')

                    if res[i][1]==opponent:
                        head_to_head[f'{team_name}'].append(goals)
                        head_to_head[f'{opponent}'].append(int(res[i][3]))

            except:
                continue

    finally:
        driver.quit()

    return goals_scored, head_to_head