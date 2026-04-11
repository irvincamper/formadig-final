import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Capture console messages
        page.on('console', lambda msg: print(f'CONSOLE [{msg.type}]: {msg.text}'))
        page.on('pageerror', lambda err: print(f'PAGE ERROR: {err}'))
        
        print('Navigating to login to set localStorage...')
        await page.goto('http://localhost:8000/modulos/login/vistas/login.html')
        
        # Set localStorage directly to simulate login
        await page.evaluate('''() => {
            localStorage.setItem('supabase_token', 'fake-token-123');
            localStorage.setItem('user_role', 'admin');
            localStorage.setItem('user_fullname', 'Administrador Playwright');
        }''')
        
        print('Navigating to dashboard...')
        await page.goto('http://localhost:8000/dashboard.html')
        await page.wait_for_timeout(2000)
        
        print('DASHBOARD DOM:')
        header_exists = await page.evaluate('() => !!document.querySelector(".header")')
        sidebar_html = await page.evaluate('() => document.getElementById("sidebarMenu").innerHTML')
        print(f'Header Exists: {header_exists}')
        print(f'Sidebar HTML Length: {len(sidebar_html)}')
        
        if len(sidebar_html) > 0:
             print('Sidebar Head:', sidebar_html[:100])
             
        # Check if the header actually has height and position
        header_rect = await page.evaluate('() => document.querySelector(".header") ? JSON.stringify(document.querySelector(".header").getBoundingClientRect()) : "null"')
        sidebar_rect = await page.evaluate('() => document.querySelector(".sidebar") ? JSON.stringify(document.querySelector(".sidebar").getBoundingClientRect()) : "null"')
        print(f'Header Rect: {header_rect}')
        print(f'Sidebar Rect: {sidebar_rect}')

        print('\nNavigating to admin_desayunos_frios...')
        await page.goto('http://localhost:8000/modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html')
        await page.wait_for_timeout(2000)
        
        header_exists = await page.evaluate('() => !!document.querySelector(".header")')
        sidebar_html = await page.evaluate('() => document.getElementById("sidebarMenu").innerHTML')
        print(f'Header Exists: {header_exists}')
        print(f'Sidebar HTML Length: {len(sidebar_html)}')
        
        header_rect = await page.evaluate('() => document.querySelector(".header") ? JSON.stringify(document.querySelector(".header").getBoundingClientRect()) : "null"')
        sidebar_rect = await page.evaluate('() => document.querySelector(".sidebar") ? JSON.stringify(document.querySelector(".sidebar").getBoundingClientRect()) : "null"')
        print(f'Header Rect: {header_rect}')
        print(f'Sidebar Rect: {sidebar_rect}')

        await browser.close()

asyncio.run(main())
