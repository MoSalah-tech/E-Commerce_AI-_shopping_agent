import asyncio
import nest_asyncio
from collections import Counter
from playwright.async_api import async_playwright
async def run():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto("https://yandex.com/images/")

                await page.wait_for_timeout(300)

                # click upload button (safe fallback)
                for selector in [
                    'button[aria-label="Search by image"]',
                    '.SearchForm-ImageSearchButton',
                    '[class="ImageSearch"]',
                    'button[class="image"]',
                ]:
                    try:
                        await page.click(selector, timeout=800)
                        break
                    except:
                        continue

                await page.wait_for_timeout(1000)

                file_input = page.locator('input[type="file"]').first
                await file_input.set_input_files(example_img)

                await page.wait_for_timeout(3000)

                text = await page.inner_text("body")

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(text)

                print("DONE")

            except Exception as e:
                print("ERROR:", e)

            finally:
                await browser.close()