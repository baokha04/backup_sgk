import asyncio
from app.services.cloudflare_client import get_cloudflare_client
from app.services.downloader import download_book_images

async def main():
    client = get_cloudflare_client()
    print("Fetching books...")
    try:
        books = await client.get_books()
        if not books:
            print("No books found.")
            return
            
        first_book = books[0]
        print(f"Testing download for Book ID: {first_book.id}")
        
        print("Starting download (limit 1 file)...")
        await download_book_images(first_book.id, limit=1)
        
        print("Done! Check the 'download' folder and 'download.log'")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
