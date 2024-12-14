import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def read_tokens():
    """Read tokens from Tokens.txt."""
    with open("Tokens.txt", "r") as file:
        return [line.strip() for line in file.readlines()]


def read_servers():
    """Read server invite links from Server.txt."""
    with open("Server.txt", "r") as file:
        return [line.strip() for line in file.readlines()]


def token_login(token, attempt_number):
    """Login to Discord using the provided token."""
    options = Options()
    options.add_argument("--headless")  # Use headless mode for better performance
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Automatically manage ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # JavaScript to log in to Discord using the provided token
    script = f"""
    function login(token) {{
        setInterval(() => {{
            document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`
        }}, 50);
        setTimeout(() => {{
            location.reload();
        }}, 2500);
    }}
    login("{token}");
    """

    try:
        # Navigate to Discord login page
        driver.get("https://discord.com/login")
        time.sleep(5)  # Wait for the login page to load

        # Execute login script
        driver.execute_script(script)
        time.sleep(5)  # Allow time for the page to reload after login

        # Check if login was successful
        if "channels" in driver.current_url:
            print(f"Account #{attempt_number} successfully logged in.")
        else:
            print(f"Login failed for token #{attempt_number}: {token[:4]}****")

        return driver

    except Exception as e:
        print(f"Error logging in with token #{attempt_number}: {e}")
        driver.quit()
        return None


def join_servers(driver, attempt_number):
    """Join servers from the list after logging in."""
    try:
        invite_links = read_servers()  # Get server invites from Server.txt
        joined_servers = []

        for invite in invite_links:
            try:
                # Navigate to the invite link
                driver.get(invite)
                time.sleep(3)  # Wait a bit to ensure the server page loads properly

                # Locate and click the "Accept Invite" button, if it exists
                try:
                    accept_button = driver.find_element("xpath", '//button[contains(text(), "Accept Invite")]')
                    accept_button.click()
                    time.sleep(2)  # Allow time for the action to process
                    
                    # Check if the join was successful
                    if "You are already a member of this server" in driver.page_source:
                        print(f"Account #{attempt_number} already in server: {invite}")
                        joined_servers.append(f"Already in server: {invite}")
                    else:
                        print(f"Account #{attempt_number} successfully joined server: {invite}")
                        joined_servers.append(f"Successfully joined: {invite}")
                except Exception:
                    # Handle cases where the invite is invalid or the account cannot join
                    if "You are already a member of this server" in driver.page_source:
                        print(f"Account #{attempt_number} already in server: {invite}")
                        joined_servers.append(f"Already in server: {invite}")
                    else:
                        print(f"Error: Couldn't join server: {invite}")
                        joined_servers.append(f"Failed to join: {invite}")
            except Exception as e:
                print(f"Error occurred while trying to join server {invite}: {e}")
                joined_servers.append(f"Error joining {invite}: {e}")

        # Print summary of server join attempts
        for server in joined_servers:
            print(server)

    except Exception as e:
        print(f"An error occurred while trying to join servers: {e}")


def main():
    """Main function to log in accounts and optionally join servers."""
    print("Discord Automation Script")
    print("1. Login to accounts and join servers")
    print("2. Exit")

    choice = input("Enter your choice: ")
    if choice == "2":
        print("Exiting.")
        return

    # Read tokens from Tokens.txt
    tokens = read_tokens()
    drivers = []  # Store WebDriver instances for logged-in accounts

    print("Logging in accounts...")
    for i, token in enumerate(tokens, start=1):
        driver = token_login(token, i)
        if driver:
            drivers.append((driver, i))  # Save the driver and account number

    # Ask to proceed with joining servers
    if drivers:
        proceed = input("Do you want to join servers with these accounts? (y/n): ").lower()
        if proceed == "y":
            for driver, account_number in drivers:
                join_servers(driver, account_number)

    # Close all WebDriver instances
    for driver, _ in drivers:
        driver.quit()

    print("Process completed.")


if __name__ == "__main__":
    main()
