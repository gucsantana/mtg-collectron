<template>
  <v-app-bar color="primary">
    <v-btn @click="$emit('back')">
      <v-icon icon="mdi-arrow-left" size="x-large" />
      <span class="ml-2">Back to Collection</span>
    </v-btn>
    <v-spacer />
    <span class="decklist_page_title">Decklist Finder</span>
    <v-spacer />
    <v-btn icon="mdi-menu" aria-label="Open settings" @click="$emit('open-settings')" />
  </v-app-bar>
  <v-main class="decklist_page_main">
    <v-container class="decklist_page_content">
      <v-card class="decklist_input_panel">
        <v-card-title>Find cards for a deck in your collection</v-card-title>
        <v-card-text>
          <p class="decklist_help_text">
            Check out which cards and printings you already have for your new deck! Paste one card per line.
          </p>
          <p class="decklist_help_text">
            Use Moxfield syntax (for example, "1 Loran's Escape (BRO) *F*") to find a specific printing, or MTGO syntax (for example, "1 Mox Diamond") to use any printing.
          </p>
          <v-radio-group v-model="priority" inline density="compact" hide-details
            class="decklist_finder_radio_options">
            <v-radio color="primary" label="Prioritize Oldest Printing" value="oldest" />
            <v-radio color="primary" label="Prioritize Newest Printing" value="newest" />
          </v-radio-group>
          <v-textarea v-model="decklist" label="Decklist" placeholder="1 Card Name" rows="8"
            variant="outlined" />
          <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>
          <v-btn color="primary" :loading="loading" :disabled="!decklist.trim()" @click="performDecklistFinderSearch">
            Find List
          </v-btn>
        </v-card-text>
      </v-card>

      <v-card v-if="results.length >= 1" class="decklist_results_panel">
        <v-card-title>Search Results</v-card-title>
        <v-card-text>
          <v-alert v-if="searched && !loading && !error && results.length === 0" type="info" variant="tonal">
            There are no matching cards to display.
          </v-alert>
          <v-list v-else-if="orderedResults.length" nav>
            <TransitionGroup name="decklist-result" tag="div" class="decklist_result_items">
              <v-list-item v-for="card in orderedResults" :key="card.resultId"
                class="decklist_result_item"
                :class="darkMode ? 'tertiary_hover_dark' : 'tertiary_hover_light'"
                @mouseenter="setHoveredCard($event, card.image)" @mouseleave="hoveredCardImage = ''">
                <template #prepend>
                  <v-tooltip text="Mark as done, removing from list" location="top" :open-delay="700">
                    <template #activator="{ props }">
                      <v-icon v-bind="props" icon="mdi-check-bold" color="primary"
                        @click.stop="markCardAsDone(card)" />
                    </template>
                  </v-tooltip>
                  <v-tooltip text="Skip this printing, tries to use next printings if available" location="top"
                    :open-delay="700">
                    <template #activator="{ props }">
                      <v-icon v-bind="props" icon="mdi-debug-step-over" color="primary" class="ml-2"
                        @click.stop="skipCard(card)" />
                    </template>
                  </v-tooltip>
                </template>
                <v-list-item-title>{{ card.amount }}x {{ card.formattedCardName }}</v-list-item-title>
              </v-list-item>
            </TransitionGroup>
          </v-list>
        </v-card-text>
      </v-card>
      <v-snackbar v-model="noMorePrintings" :timeout="3500">No more printings of this card in your collection!</v-snackbar>
      <v-img v-if="hoveredCardImage" :src="hoveredCardImage" class="hover_card_image rounded-lg"
        :style="{ top: `${mouseCoords.y + 20}px`, left: `${mouseCoords.x + 30}px` }" />
    </v-container>
  </v-main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { authFetch } from './authFetch.js'

const props = defineProps({
  userId: { type: [String, Number], required: true },
  darkMode: { type: Boolean, default: false },
  csrfToken: { type: String, required: true },
  setList: { type: Array, required: true },
})
defineEmits(['back', 'open-settings'])

const decklist = ref('')
const priority = ref('oldest')
const loading = ref(false)
const searched = ref(false)
const error = ref('')
const noMorePrintings = ref(false)
const searchlist = ref([])
const allResults = ref([])
const results = ref([])
const orderedResults = computed(() => [...results.value].sort(compareByReleaseAndNumber))
const hoveredCardImage = ref('')
const mouseCoords = ref({ x: 0, y: 0 })

function normalizeCardName(name) {
  const normalized = name.toLowerCase().replaceAll('//', '/')
  return normalized
}

function matchesCardName(candidate, requested) {
  const normalizedCandidate = normalizeCardName(candidate)
  const normalizedRequested = normalizeCardName(requested)
  return normalizedCandidate === normalizedRequested ||
    normalizedCandidate.split('/')[0].trim() === normalizedRequested
}

function compareByReleaseAndNumber(a, b) {
  const firstRelease = Date.parse(a.releaseDate)
  const secondRelease = Date.parse(b.releaseDate)
  if (Number.isFinite(firstRelease) && Number.isFinite(secondRelease) && firstRelease !== secondRelease) {
    return priority.value === 'newest'
      ? secondRelease - firstRelease
      : firstRelease - secondRelease
  }
  if (Number.isFinite(firstRelease) !== Number.isFinite(secondRelease)) {
    return Number.isFinite(firstRelease) ? -1 : 1
  }
  if (a.cardSet !== b.cardSet) return a.cardSet.localeCompare(b.cardSet)
  return (parseInt(a.collectorNumber.replace(/\D/g, ''), 10) || 0) -
    (parseInt(b.collectorNumber.replace(/\D/g, ''), 10) || 0)
}

function getCardImage(card) {
  const imageUris = card.image_uris ?? card.card_faces?.[0]?.image_uris
  return imageUris?.normal
}

async function getOwnedPrintings(cardName) {
  const response = await authFetch('/mtg-collectron/owncard/byname', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': props.csrfToken,
    },
    body: JSON.stringify({
      card_owner_id: props.userId,
      card_name: cardName,
    }),
  })
  if (!response.ok) {
    throw new Error(`Unable to search your collection for "${cardName}" (HTTP ${response.status}).`)
  }

  const ownedCards = await response.json()
  if (!Array.isArray(ownedCards)) {
    throw new Error('The card-finder endpoint did not return a list.')
  }
  return ownedCards
}

async function getCardsForSet(setCode, setCache) {
  if (!setCache.has(setCode)) {
    const response = await authFetch(`/mtg-collectron/card/${encodeURIComponent(setCode.toLowerCase())}`, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`Unable to load card data for set "${setCode}" (HTTP ${response.status}).`)
    }

    const cards = await response.json()
    if (!Array.isArray(cards)) {
      throw new Error(`The card endpoint for set "${setCode}" did not return a list.`)
    }
    setCache.set(setCode, cards)
  }
  return setCache.get(setCode)
}

async function findCardsForRequest(request, setCache) {
  const ownedCards = await getOwnedPrintings(request.name)
  const matchingOwnedCards = ownedCards.filter(ownedCard => {
    if (
      !ownedCard ||
      typeof ownedCard.card_name !== 'string' ||
      typeof ownedCard.set_code !== 'string' ||
      typeof ownedCard.collector_number !== 'string' ||
      ownedCard.card_count == null ||
      !Number.isSafeInteger(Number(ownedCard.card_count)) ||
      Number(ownedCard.card_count) < 0
    ) {
      throw new Error('The card-finder response contains an invalid card.')
    }
    return matchesCardName(ownedCard.card_name, request.name) &&
      (!request.set || ownedCard.set_code.toLowerCase() === request.set) &&
      (!request.collectorNumber || ownedCard.collector_number === request.collectorNumber)
  })

  const cardsBySet = new Map()
  for (const ownedCard of matchingOwnedCards) {
    if (!cardsBySet.has(ownedCard.set_code)) {
      cardsBySet.set(ownedCard.set_code, await getCardsForSet(ownedCard.set_code, setCache))
    }
  }

  const printings = []
  for (const ownedCard of matchingOwnedCards) {
    const cardData = cardsBySet.get(ownedCard.set_code).find(card =>
      card.name === ownedCard.card_name &&
      String(card.collector_number) === ownedCard.collector_number,
    )
    if (!cardData) {
      throw new Error(
        `Card data for "${ownedCard.card_name}" (${ownedCard.set_code}-${ownedCard.collector_number}) was not found.`,
      )
    }
    const setInfo = props.setList.find(set =>
      typeof set.code === 'string' && set.code.toLowerCase() === ownedCard.set_code.toLowerCase(),
    )
    if (!setInfo?.released_at) {
      throw new Error(`Release date for set "${ownedCard.set_code}" was not found.`)
    }

    const tags = [
      ownedCard.is_tagged_square ? '■' : '',
      ownedCard.is_tagged_triangle ? '▲' : '',
      ownedCard.is_tagged_circle ? '⚫︎' : '',
      ownedCard.is_tagged_cross ? '✖' : '',
    ].join('')
    const image = getCardImage(cardData)
    printings.push({
      resultId: `${ownedCard.set_code}-${ownedCard.collector_number}`,
      cardName: ownedCard.card_name,
      cardSet: ownedCard.set_code,
      collectorNumber: ownedCard.collector_number,
      releaseDate: setInfo.released_at,
      amount: Number(ownedCard.card_count),
      formattedCardName:
        `${ownedCard.card_name} (${ownedCard.set_code.toUpperCase()}-${ownedCard.collector_number}) ${tags}`,
      image,
    })
  }
  return printings.sort(compareByReleaseAndNumber)
}

function parseDecklistLine(line) {
  const trimmedLine = line.trim()
  if (!trimmedLine) return null
  const elements = trimmedLine.split(' (')
  const firstPart = elements[0]
  const firstSpace = firstPart.indexOf(' ')
  const amount = Number.parseInt(firstSpace === -1 ? firstPart : firstPart.slice(0, firstSpace), 10)
  if (!Number.isSafeInteger(amount) || amount <= 0 || firstSpace === -1) return null
  
  const request = {
    name: firstPart.slice(firstSpace + 1).trim().replace("/"," // "), // the 'export for MTGO' exports with one / instead of //
    amount,
    set: '',
    collectorNumber: '',
  }
  console.log("request.name",request.name)
  if (!request.name) return null

  if (elements.length > 1) {
    const closingParen = elements[1].indexOf(')')
    const set = elements[1].slice(0, closingParen === -1 ? undefined : closingParen).trim()
    const printingDetails = closingParen === -1 ? '' : elements[1].slice(closingParen + 1).trim()
    const collectorNumber = printingDetails?.split(' ')[0]
    request.set = set.toLowerCase()
    request.collectorNumber = collectorNumber && /^\d/.test(collectorNumber) ? collectorNumber : ''
  }
  return request
}

function selectEnoughCards(cards, amount) {
  let total = 0
  const selected = []
  for (const card of cards) {
    const selectedAmount = Math.min(card.amount, amount - total)
    if (selectedAmount <= 0) break
    selected.push({ ...card, amount: selectedAmount })
    total += selectedAmount
    if (total >= amount) break
  }
  return total >= amount ? selected : []
}

watch(priority, () => {
  results.value = searchlist.value.flatMap(request =>
    selectEnoughCards(
      allResults.value
        .filter(card => card.requestId === request.id)
        .sort(compareByReleaseAndNumber),
      request.amount,
    ),
  )
  results.value.sort(compareByReleaseAndNumber)
})

async function performDecklistFinderSearch() {
  loading.value = true
  error.value = ''
  noMorePrintings.value = false
  searched.value = true
  searchlist.value = []
  allResults.value = []
  results.value = []

  try {
    const requests = []
    const invalidLines = []
    for (const line of decklist.value.split(/\r?\n/)) {
      const request = parseDecklistLine(line)
      if (request) {
        requests.push(request)
      } else if (line.trim()) {
        invalidLines.push(line.trim())
      }
    }

    const setCache = new Map()
    const searchErrors = []
    for (const request of requests) {
      try {
        const printings = await findCardsForRequest(request, setCache)
        const selected = selectEnoughCards(printings, request.amount)
        if (selected.length) {
          request.id = `request-${searchlist.value.length}`
          searchlist.value.push(request)
          allResults.value.push(...printings.map(card => ({
            ...card,
            requestId: request.id,
            resultId: `${request.id}-${card.resultId}`,
          })))
          results.value.push(...selected.map(card => ({
            ...card,
            requestId: request.id,
            resultId: `${request.id}-${card.resultId}`,
          })))
        }
      } catch (requestError) {
        searchErrors.push(requestError instanceof Error
          ? requestError.message
          : `Unable to search for "${request.name}".`)
      }
    }
    results.value.sort(compareByReleaseAndNumber)
    if (invalidLines.length) {
      searchErrors.unshift(`Could not parse these lines: ${invalidLines.join('; ')}`)
    }
    error.value = searchErrors.join(' ')
  } catch (searchError) {
    error.value = searchError instanceof Error
      ? searchError.message
      : 'Unable to search your collection. Please try again.'
  } finally {
    loading.value = false
  }
}

function markCardAsDone(card) {
  hoveredCardImage.value = ''
  results.value = results.value.filter(result => result.resultId !== card.resultId)
  allResults.value = allResults.value.filter(result => result.resultId !== card.resultId)
  const request = searchlist.value.find(item => item.id === card.requestId)
  if (request) {
    request.amount -= card.amount
    if (request.amount <= 0) {
      searchlist.value = searchlist.value.filter(item => item.id !== request.id)
    }
  }
  console.log("searchlist.value",searchlist.value)
}

function skipCard(card) {
  hoveredCardImage.value = ''
  allResults.value = allResults.value.filter(result => result.resultId !== card.resultId)
  const request = searchlist.value.find(item => item.id === card.requestId)
  if (!request) return

  const remaining = selectEnoughCards(
    allResults.value.filter(result => result.requestId === request.id),
    request.amount,
  )
  results.value = results.value.filter(result => result.requestId !== request.id)
  if (remaining.length) {
    results.value.push(...remaining)
    results.value.sort(compareByReleaseAndNumber)
  } else {
    searchlist.value = searchlist.value.filter(item => item.id !== request.id)
    noMorePrintings.value = true
  }
}

function setHoveredCard(event, image) {
  if (!image) return
  mouseCoords.value = { x: event.clientX, y: event.clientY }
  hoveredCardImage.value = image
}
</script>

<style scoped>
.decklist_page_main {
  margin: 0 auto;
  width: 100%;
  max-width: 900px;
}

.decklist_page_content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 30px;
  padding-bottom: 40px;
}

.decklist_input_panel,
.decklist_results_panel {
  width: 100%;
  padding: 8px 20px;
}

.decklist_help_text {
  margin-bottom: 16px;
}

.decklist_finder_radio_options :deep(.v-selection-control-group) {
  column-gap: 8px;
  margin-bottom: 20px;
  align-self: center;
}

.decklist_results_separator {
  opacity: 0.8;
}

.decklist_result_item.v-list-item {
  --v-list-item-min-height: 30px;
  height: 30px !important;
  min-height: 30px !important;
  padding-block: 0 !important;
}

.decklist_result_item.v-list-item :deep(.v-list-item__prepend) {
  min-height: 30px;
}

.decklist_result_items {
  position: relative;
}

.decklist_result_items :deep(.decklist-result-enter-active),
.decklist_result_items :deep(.decklist-result-leave-active) {
  transition: opacity 220ms ease, transform 220ms ease;
}

.decklist_result_items :deep(.decklist-result-enter-from) {
  opacity: 0;
  transform: translateX(-20px);
}

.decklist_result_items :deep(.decklist-result-leave-to) {
  opacity: 0;
  transform: translateX(48px);
}

.decklist_result_items :deep(.decklist-result-leave-active) {
  position: absolute;
  width: 100%;
  z-index: 1;
}

.decklist_result_items :deep(.decklist-result-move) {
  transition: transform 220ms ease;
}

.decklist_page_title {
  font-size: 1.2rem;
  font-weight: 500;
}

.tertiary_hover_light:hover {
  background-color: #FFC0CA;
}

.tertiary_hover_dark:hover {
  background-color: #BDD8FB;
  color: black;
}

.hover_card_image {
  position: fixed;
  width: 100%;
  max-width: 200px;
  z-index: 99999;
}

@media (max-width: 600px) {
  .decklist_page_title {
    display: none;
  }

  .decklist_page_content {
    padding: 16px 8px 24px;
  }

  .decklist_input_panel,
  .decklist_results_panel {
    padding: 8px;
  }
}
</style>
