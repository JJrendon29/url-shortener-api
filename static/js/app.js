const slider = document.getElementById('expiry-slider')
    const display = document.getElementById('expiry-display')

    function formatHours(h) {
      h = parseInt(h)
      if (h < 24) return h === 1 ? '1 hora' : h + ' horas'
      const days = Math.floor(h / 24)
      return days === 1 ? '1 día' : days + ' días'
    }

    slider.addEventListener('input', () => {
      display.textContent = formatHours(slider.value)
    })

    let currentCode = null

    async function shortenUrl() {
      const urlInput = document.getElementById('url-input')
      const btn = document.getElementById('shorten-btn')
      const errorMsg = document.getElementById('error-msg')
      const resultCard = document.getElementById('result-card')

      errorMsg.classList.remove('visible')
      resultCard.classList.remove('visible')

      const url = urlInput.value.trim()
      if (!url) {
        showError('Ingresá una URL válida.')
        return
      }

      btn.disabled = true
      btn.textContent = 'Acortando...'

      try {
        const response = await fetch('/urls', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            original_url: url,
            expires_in_hours: parseInt(slider.value)
          })
        })

        const data = await response.json()

        if (!response.ok) {
          showError(data.detail || 'Ocurrió un error.')
          return
        }

        currentCode = data.code
        document.getElementById('short-url-display').textContent = data.short_url
        document.getElementById('stat-clicks').textContent = data.clicks
        document.getElementById('stat-code').textContent = data.code
        document.getElementById('stat-expiry').textContent = formatHours(slider.value)

        resultCard.classList.add('visible')
        urlInput.value = ''

      } catch (e) {
        showError('No se pudo conectar con el servidor.')
      } finally {
        btn.disabled = false
        btn.textContent = 'Acortar URL'
      }
    }

    function showError(msg) {
      const el = document.getElementById('error-msg')
      el.textContent = msg
      el.classList.add('visible')
    }

    function copyUrl() {
      const text = document.getElementById('short-url-display').textContent
        
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
          showCopied()
        })
      } else {
        const textarea = document.createElement('textarea')
        textarea.value = text
        textarea.style.position = 'fixed'
        textarea.style.opacity = '0'
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand('copy')
        document.body.removeChild(textarea)
        showCopied()
      }
    }
    
    function showCopied() {
      const btn = document.getElementById('copy-btn')
      btn.textContent = '¡Copiado!'
      setTimeout(() => { btn.textContent = 'Copiar' }, 1500)
    }

    document.getElementById('url-input').addEventListener('keydown', e => {
      if (e.key === 'Enter') shortenUrl()
    })