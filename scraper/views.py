from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from bs4 import BeautifulSoup
from .forms import ScrapeForm
from .models import ScrapeHistory
from datetime import datetime
import urllib.parse

def index(request):
    form = ScrapeForm(request.POST or None)
    recent_scrapes = ScrapeHistory.objects.all().order_by('-scraped_at')[:6]

    if request.method == 'POST' and form.is_valid():
        url = form.cleaned_data['url']
        # Create a pending record
        scrape_history = ScrapeHistory.objects.create(
            url=url,
            title='Pending Scrape',
            status='pending',
            content_json={}
        )
        try:
            headers = {'User-Agent': 'DjangoWebScraper/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract data
            title = soup.title.string if soup.title else 'No Title'
            description = soup.find('meta', attrs={'name': 'description'})
            description = description['content'] if description else ''
            headings = [{'tag': tag.name, 'text': tag.get_text(strip=True)} for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
            links = [{'url': urllib.parse.urljoin(url, a.get('href')), 'text': a.get_text(strip=True) or 'No text'} for a in soup.find_all('a', href=True)]
            images = [{'src': urllib.parse.urljoin(url, img.get('src')), 'alt': img.get('alt', 'No alt text')} for img in soup.find_all('img', src=True)]
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]

            # Update content_json
            content_json = {
                'title': title,
                'description': description,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'headings': headings,
                'links': links,
                'images': images,
                'paragraphs': paragraphs,
                'total_links': len(links),
                'total_images': len(images),
                'total_paragraphs': len(paragraphs),
            }

            # Update the record
            scrape_history.title = title
            scrape_history.status = 'success'
            scrape_history.content_json = content_json
            scrape_history.error_message = ''
            scrape_history.save()

            messages.success(request, 'Website scraped successfully!')
            return redirect('results', pk=scrape_history.pk)

        except requests.exceptions.RequestException as e:
            scrape_history.status = 'failed'
            scrape_history.error_message = str(e)
            scrape_history.save()
            messages.error(request, f'Error scraping URL: {str(e)}')

    return render(request, 'scraper/index.html', {
        'form': form,
        'recent_scrapes': recent_scrapes
    })

def results(request, pk):
    try:
        scrape_history = ScrapeHistory.objects.get(pk=pk)
        if scrape_history.status == 'failed':
            messages.error(request, f'Scrape failed: {scrape_history.error_message}')
    except ScrapeHistory.DoesNotExist:
        messages.error(request, 'Scrape record not found.')
        return redirect('index')
    return render(request, 'scraper/results.html', {'scrape_history': scrape_history})