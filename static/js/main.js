const script = document.getElementById('search-js')
const locationInput = document.getElementById('pick-up')
const destinationInput = document.getElementById('destination')
document.querySelector('[autocomplete~="street-address"]') != null

let lastFocusedInput = null

locationInput.addEventListener('focus', () => {
  lastFocusedInput = locationInput
})

destinationInput.addEventListener('focus', () => {
  lastFocusedInput = destinationInput
})

script.onload = function () {
  const autoFill = mapboxsearch.autofill({
    accessToken: token,
    options: { country: 'za' },
  })

  autoFill.addEventListener('retrieve', async (e) => {
    const address = e.detail.features[0].properties.full_address
    if (lastFocusedInput === locationInput && locationInput.value) {
      console.log('location', address)
      locationInput.value = await address
    } else if (
      lastFocusedInput === destinationInput &&
      destinationInput.value
    ) {
      console.log('destination', address)
      destinationInput.value = await address
    }
  })
}
