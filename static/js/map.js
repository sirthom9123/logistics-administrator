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
      locationInput.value = await address
    } else if (
      lastFocusedInput === destinationInput &&
      destinationInput.value
    ) {
      destinationInput.value = await address
    }
  })
}

const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value
const form = document.getElementById('location-form')
const alertBox = document.getElementById('alert-box')
const testimonialBody = document.getElementById('distance-results')

const handleAlerts = (type, msg) => {
  alertBox.innerHTML = `
  <div class="alert alert-${type}" role="alert">
      ${msg}
  </div>
  `
}

form.addEventListener('submit', async (e) => {
  e.preventDefault()

  const formData = new FormData(form)
  try {
    const response = await fetch(
      '/cost_estimates/?' + new URLSearchParams(formData).toString()
    )
    const data = await response.json()
    console.log(data.location)
    testimonialBody.innerHTML = `
      <div class="testimonial-cat mb-30">
        <h5>Travelling from ${data.location} <br />To: <br /> ${data.destination}</h5>
      </div>
      <div class="testimonial-content mb-45">
        <p class="card-text mb-5">
          Service fee = R${data.cost}
        </p>
        <button
          type="button"
          class="btn btn-warning"
          data-toggle="modal"
          data-target="#staticBackdrop"
          style="background-color: #055808"
        >
          Accept
        </button>
        <a
          class="btn btn-danger"
          href="/"
          style="float: right; background-color: #990505"
          >Decline</a
        >
      </div>
      `
  } catch (error) {
    console.error(error)
    handleAlerts('danger', error.message)
  }
})
