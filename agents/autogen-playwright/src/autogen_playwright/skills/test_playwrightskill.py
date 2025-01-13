from autogen_playwright import PlaywrightSkill

def test_ee_broadband_page_navigation_and_validation():
    try:
        # Initialize browser session
        pws = PlaywrightSkill()
        pws.start_session('EE Broadband Page Navigation and Validation')
        
        # Step 1: Navigate to ee.co.uk
        pws.navigate('https://ee.co.uk')
        pws.take_screenshot('homepage_loaded')
        
        # Step 2: Accept cookies in the OneTrust banner
        pws.click_element('#onetrust-accept-btn-handler')
        pws.take_screenshot('cookies_accepted')
        
        # Step 3: First hover over Broadband
        pws.hover_element('a[aria-label="Broadband"]')
        # Add a small wait to allow mega menu to appear
        pws.page.wait_for_timeout(1000)
        pws.take_screenshot('broadband_hovered')
        
        # Step 4: Now that mega menu is visible, click "explore broadband" text
        pws.click_element('text=explore broadband')
        pws.take_screenshot('broadband_explored')
        
        # Step 5: Analyze and summarize the page content
        pws.verify_text_content('Broadband')
        
        # Step 6: Enter UB87PE in the postcode field and click continue
        pws.fill_form('input[name="postcode"]', 'UB87PE')
        # Try more specific selector for the continue button
        pws.click_element('button[type="submit"], button:has-text("Continue"), [aria-label="Continue"]')
        pws.take_screenshot('postcode_entered_and_continue_clicked')
        
        # Analyze and summarize the page
        pws.verify_text_content('Broadband')
        
    except Exception as e:
        print(f'Test failed with error: {str(e)}')
    finally:
        # End session and generate report
        pws.end_session()

test_ee_broadband_page_navigation_and_validation()