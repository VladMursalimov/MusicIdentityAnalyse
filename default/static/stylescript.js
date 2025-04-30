let currentTracks = []; // Сохраняем полученные треки для последующего анализа

 async function getTracks() {
      const userId = document.getElementById('user-id').value;
      const resultDiv = document.getElementById('result');
      const tracksDisplay = document.getElementById('tracks-display');

      resultDiv.innerHTML = '<p>Получаем ваши любимые треки...</p>';
      tracksDisplay.style.display = 'none';

      try {
        const response = await fetch('/get-tracks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ user_id: userId })
        });

        if (!response.ok) {
          const error = await response.json();
          resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${error.error}</p>`;
          return;
        }

        const data = await response.json();
        currentTracks = data.tracks; // Сохраняем треки для анализа

        // Обновляем блок с треками
        let tracksHtml = '<div class="track-header">Ваши треки</div>';
        data.tracks.forEach((track, index) => {
          tracksHtml += `
            <div class="track-item">
              <div class="track-title">${track.track}</div>
              <div class="track-artist">${track.artist}</div>
            </div>
          `;
          if (index < data.tracks.length - 1) {
            tracksHtml += '<div class="track-separator"></div>';
          }
        });

        tracksDisplay.innerHTML = tracksHtml;
        tracksDisplay.style.display = 'block';
        resultDiv.innerHTML = '';

      } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Ошибка: ${error.message}</p>`;
      }
    }


async function analyzeTracks() {
      if (!currentTracks || currentTracks.length === 0) {
        alert('Сначала получите треки!');
        return;
      }

      const resultDiv = document.getElementById('result');
      const progressContainer = document.getElementById('progress-container');
      const progressBar = document.getElementById('progress-bar');
      const progressText = document.getElementById('progress-text');

      // Показываем прогресс бар
      progressContainer.style.display = 'block';
      progressBar.style.width = '0%';

      // Анимация прогресса
      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress > 90) progress = 90; // Не доходим до 100% пока не завершится запрос
        progressBar.style.width = `${progress}%`;
      }, 300);

      try {
        const response = await fetch('/analyze-tracks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ tracks: currentTracks })
        });

        if (!response.ok) {
          const error = await response.text();
          clearInterval(progressInterval);
          progressContainer.style.display = 'none';
          resultDiv.innerHTML += `<p style="color: red;">Ошибка анализа: ${error}</p>`;
          return;
        }

        // Завершаем анимацию прогресса
        clearInterval(progressInterval);
        progressBar.style.width = '100%';

        // Читаем потоковый ответ
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let resultText = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          resultText += chunk;

          // Создаем элемент для отображения если его нет
          let streamingElement = document.getElementById('streaming-analysis');
          if (!streamingElement) {
            streamingElement = document.createElement('div');
            streamingElement.id = 'streaming-analysis';
            resultDiv.appendChild(streamingElement);
          }

          streamingElement.innerHTML = convertMarkdownToHTML(resultText);
          streamingElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }

        setTimeout(() => {
          progressContainer.style.display = 'none';
        }, 500);

      } catch (error) {
        clearInterval(progressInterval);
        progressContainer.style.display = 'none';
        resultDiv.innerHTML += `<p style="color: red;">Ошибка анализа: ${error.message}</p>`;
      }
    }

async function getAndAnalyzeTracks() {
    await getTracks();
    showResultsWithAnimation()
    if (currentTracks && currentTracks.length > 0) {
        setTimeout(async () => {
            await analyzeTracks();
        }, 500);
    }
    const analyzingMsg = document.getElementById('analyzing-message');
    if (analyzingMsg) analyzingMsg.remove();
}

function convertMarkdownToHTML(text) {
      text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
      text = text.replace(/^# (.*)/gm, '<h4>$1</h4>');
      text = text.replace(/\n\n/g, '</p><p>');
      text = `<p>${text}</p>`;

      return text;
    }


function showResultsWithAnimation() {
      const tracksDisplay = document.getElementById('tracks-display');
      const resultBox = document.getElementById('result');

      // Показываем блоки
      tracksDisplay.style.display = 'block';
      resultBox.style.display = 'block';

      // Сбрасываем анимацию (на случай повторного вызова)
      tracksDisplay.style.animation = 'none';
      resultBox.style.animation = 'none';

      // Принудительный рефлоу для сброса анимации
      void tracksDisplay.offsetWidth;
      void resultBox.offsetWidth;

      // Применяем анимацию снова
      tracksDisplay.style.animation = 'fadeInUp 0.5s ease-out forwards';
      tracksDisplay.style.animationDelay = '0.3s';
      resultBox.style.animation = 'fadeInUp 0.5s ease-out forwards';
      resultBox.style.animationDelay = '0.5s';
    }