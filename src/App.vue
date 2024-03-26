<template>
  <v-app>
    <v-overlay :model-value="loading" class="align-center justify-center">
      <v-progress-circular color="primary" indeterminate size="64"/>
    </v-overlay>
    <v-overlay persistent :model-value="import_window_active" class="align-center justify-center">
      <v-card class="import_window">
        <v-card-item>
          <v-row class="import_window_header align-center">
            <v-col cols="6"><h2>Import Cards</h2></v-col>
            <v-spacer/>
            <v-col cols="1">
              <v-tooltip text="/n" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="pink-lighten-1"/>
                </template>
                <p>'Moxfield' uses the Moxfield syntax, one card per line</p>
                <p class="mb-0">e.g. "1 Loran's Escape (BRO) *F*"</p>
                <p class="mb-0">'Native' uses the JSON syntax exported by the 'Export Collection' button</p>
                <p class="mb-0">It will REWRITE the entire collection, not add to it</p>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-item>
        <v-divider/>
        <v-radio-group inline v-model="import_syntax" density="compact" hide-details style="display:inline-block;">
          <v-radio color="pink-lighten-1" label="Moxfield" value="moxfield"/>
          <v-radio color="pink-lighten-1" label="Native" value="native"/>
        </v-radio-group>
        <v-textarea v-model="import_text" class="import_text_field" variant="outlined"/>
        <v-row>
          <v-spacer/>
          <v-col cols="3"><v-btn @click="import_cards">Import</v-btn></v-col>
          <v-col cols="3"><v-btn @click="import_window_active=false">Close</v-btn></v-col>
        </v-row>
      </v-card>
    </v-overlay>
    <v-overlay :model-value="import_results_active" class="align-center justify-center">
      <v-card class="import_results_window">
        <v-card-item>
          <h2 v-show="import_success == true">Import Success</h2>
          <h2 v-show="import_success == false">Import Failure</h2>
        </v-card-item>
        <v-divider/>
        <br/>
        <p v-show="import_card_total > 0">Imported {{ import_card_total }} unique cards.</p>
        <br/>
        <p v-show="import_errors.length > 0">The following lines could not be imported:</p>
        <br/>
        <p>{{ import_errors }}</p>
      </v-card>
    </v-overlay>
    <v-overlay persistent :model-value="export_window_active" class="align-center justify-center">
      <v-card class="import_window">
        <v-card-item>
          <v-row class="import_window_header align-center">
            <v-col cols="6"><h2>Export Cards</h2></v-col>
            <v-spacer/>
            <v-col cols="1">
              <v-tooltip text="/n" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="pink-lighten-1"/>
                </template>
                <p>Exports the collection stock as a JSON file readable by this system</p>
                <p class="mb-0">Save it somewhere if you need a backup to be safe</p>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-item>
        <v-divider/>
        <v-textarea v-model="export_text" class="import_text_field" variant="outlined" :readonly="true"/>
        <v-row>
          <v-spacer/>
          <v-col cols="4"><v-btn @click="copyCollectionToClipboard">Copy to Clipboard</v-btn></v-col>
          <v-col cols="3"><v-btn @click="export_window_active=false">Close</v-btn></v-col>
        </v-row>
      </v-card>
    </v-overlay>
    <v-snackbar v-model="toast" :timeout="2000">Copied to clipboard!</v-snackbar>
    <v-app-bar color="pink-lighten-1">
      <v-btn @click="drawer = !drawer">
        <v-icon icon="mdi-chevron-right-circle" size="x-large" v-if="!drawer"/>
        <v-icon icon="mdi-chevron-left-circle" size="x-large" v-if="drawer"/>
        <p style="margin-left: 10px;">Set Navigation</p>
      </v-btn>
      <v-spacer/>
      <v-btn @click="settings = !settings">
        <v-icon icon="mdi-cog" size="x-large"/>
      </v-btn>
    </v-app-bar>
    <v-card>
      <v-navigation-drawer app v-model="drawer">
        <v-list dense>
          <v-list-item id="column_set_visib_title"><p class="column_header">Set Visibility</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="core" v-model="set_types_shown" class="set_check">
              <label for="check_core" style="display: inline-block;">Core Sets</label>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="expansion" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Expansions</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="masters" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Masters Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="commander" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Commander Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="draft_innovation" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Draft Innovation Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="masterpiece" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Masterpieces</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="all" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Other Sets</p>
          </v-list-item>
        </v-list>
        <v-list-item><p class="column_header">Search for Set</p></v-list-item>
        <v-list-item><v-text-field v-model="set_search" prepend-inner-icon="mdi-magnify" variant="outlined" density="compact"/></v-list-item>
        <v-list-item><p class="column_header">List of Sets</p></v-list-item>
        <v-list-item v-for="set in set_list"> <div @click="select_set(set)" v-show="set['digital'] == false && (set_types_shown.includes(set['set_type']) || (set_types_shown.includes('all') && !['core','expansion','commander','masters','draft_innovation','masterpiece'].includes(set['set_type']))) && (set_search == '' || set['name'].toLowerCase().includes(set_search.toLowerCase())) && (new Date().toISOString().substring(0,10) > set.released_at)" class="set_list_element" :class="{'set_list_element_selected': set.code == current_set_code }" >
          <img :src="set['icon_svg_uri']" class="set_logo" width="18px" height="18px"/>
          <p class="set_list_name">{{ set['name'] }}</p>
        </div> </v-list-item>
      </v-navigation-drawer>
    </v-card>
    <v-main v-if="current_set && current_set_base_cards">
      <v-sheet class="main_body">
        <v-card class="set_page_title_card" flat>
          <div>
            <p class="set_page_title">{{ current_set['name'] }}</p>
          </div>
          <div style="display:inline-block; margin-right: 30px;">
            <p class="set_page_subtitle">Release Date:</p><p class="set_page_subtext">{{ current_set['released_at'] }}</p>
          </div>
          <div style="display:inline-block">
            <p class="set_page_subtitle">Set Type:</p><p class="set_page_subtext">{{ current_set['set_type'] }}</p>
          </div>
        </v-card>
        <v-row>
          <v-col cols="3">
            <v-text-field v-model="card_search" label="Card Search" prepend-inner-icon="mdi-magnify" variant="outlined" color="primary" density="compact" clearable @click:clear="card_search = ''"/>
          </v-col>
          <v-spacer/>
          <v-col cols="3">
            <v-select v-model="page_options.card_per_page_option_selected" label="Cards per Page" :items="card_per_page_options" return-object density="compact" variant="outlined"/>
          </v-col>
          <v-col cols="3" v-show="false">
            <v-select v-model="page_options.show_option_selected" label="Show:" :items="show_options" return-object density="compact"/>
          </v-col>
        </v-row>
        <v-card class="page_header">
          <v-card class="set_stats_banner" flat>
            <v-row style="height: 70px;" align="center" >
              <v-col><p>Base Set:</p><p>{{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p></v-col>
              <v-divider vertical/>
              <!-- <v-col v-if="current_set_commons > 0"><p>Commons:</p><p>{{ current_set_owned_commons }}/{{ current_set_commons }}</p></v-col>
              <v-divider vertical v-if="current_set_commons > 0"/>
              <v-col v-if="current_set_uncommons > 0"><p>Uncommons:</p><p>{{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p></v-col>
              <v-divider vertical v-if="current_set_uncommons > 0"/>
                <v-col v-if="current_set_rares > 0"><p>Rares:</p><p>{{ current_set_owned_rares }}/{{ current_set_rares }}</p></v-col>
                <v-divider vertical v-if="current_set_rares > 0"/>
              <v-col v-if="current_set_mythics > 0"><p>Mythic Rares:</p><p>{{ current_set_owned_mythics }}/{{ current_set_mythics }}</p></v-col>
              <v-divider vertical v-if="current_set_mythics > 0"/> -->
              <v-col v-if="current_set_extra_cards_qty > 0">
                <p style="display:inline;">Extra Cards:</p>
                <v-tooltip text="/n" location="bottom" style="display:inline;">
                  <template v-slot:activator="{ props }">
                    <v-icon :="props" icon="mdi-help-circle" size="medium" style="margin-left:10px;"/>
                  </template>
                  <p>Showcase frame cards, extended art carts, borderless cards, Buy-a-Box, etc</p>
                </v-tooltip>
                <p>{{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p></v-col>
              <v-divider vertical v-if="current_set_extra_cards_qty > 0"/>
              <v-col><p>Grand Total:</p><p>{{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p></v-col>
              <v-col><p>Foil Cards:</p><p>{{ current_set_owned_foils }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p></v-col>
            </v-row>
          </v-card>
          <v-progress-linear height="15" v-model="getProgressForSet" :color="getProgressForSet < 100 ? 'pink-lighten-1' : 'amber-lighten-2' ">
            <template v-slot:default="{ value }">
              <strong>{{ Math.round(value * 10) / 10 }}%</strong>
            </template>
          </v-progress-linear>
        </v-card>
        <v-sheet name="normal_cards_holder">
          <v-row no-gutters>
            <v-col v-for="(item,index) in current_set_base_cards.filter((card) => (card.name.toLowerCase().includes(card_search) || card_search == '')).slice(pageSliceStart,pageSliceEnd)" cols="6" sm="6" md="4" lg="3" >
              <CardSlot :card="item" :collection_stock="collection_stock.o" :current_set_code="current_set_code" :show_option="page_options.show_option_selected.value" :is_extra="(index+pageSliceStart) >= current_set_base_cards_qty" :base_set_total="current_set_base_cards_qty" :extra_set_total="current_set_extra_cards_qty"></CardSlot>
            </v-col>
          </v-row>
        </v-sheet>
      </v-sheet>
      <v-pagination v-if="page_options.card_per_page_option_selected != 4" v-model="current_page" :length="pageCount" total-visible="8"/>
      <v-card class="set_stats_box" :elevation="10" v-scroll="on_scroll_stats_box" v-show="stats_box_visible">
        <v-card class="set_stats_inner_box" flat>
          <p>Base Set: {{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p>
          <p v-if="current_set_commons > 0">Commons: {{ current_set_owned_commons }}/{{ current_set_commons }}</p>
          <p v-if="current_set_uncommons > 0">Uncommons: {{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p>
          <p v-if="current_set_rares > 0">Rares: {{ current_set_owned_rares }}/{{ current_set_rares }}</p>
          <p v-if="current_set_mythics > 0">Mythic Rares: {{ current_set_owned_mythics }}/{{ current_set_mythics }}</p>
          <p v-if="current_set_extra_cards_qty > 0">Extra Cards: {{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p>
          <p>Grand Total: {{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p>
          <p>Foil Cards: {{ current_set_owned_foils }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p>
        </v-card>
        <v-progress-linear height="15" v-model="getProgressForSet" :color="getProgressForSet < 100 ? 'pink-lighten-1' : 'amber-lighten-2' ">
            <template v-slot:default="{ value }">
              <strong>{{ Math.round(value * 10) / 10 }}%</strong>
            </template>
          </v-progress-linear>
      </v-card>
    </v-main>
    <v-card >
      <v-navigation-drawer app temporary v-model="settings" location="right">
        <v-list dense>
          <v-list-item><p class="column_header">User Preferences</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <v-select v-model="page_options.full_set_option_selected" label="Full Set Definition" :items="full_set_options" return-object>
              <v-tooltip activator="parent" location="bottom">Defines the objective considered for the progress bars and 'full set' message displays for each set</v-tooltip>
            </v-select>
          </v-list-item>
          <v-divider/>
          <v-list-item><p class="column_header">Collection Functions</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <v-btn @click="import_window_active = true" class="side_drawer_button" density="comfortable" variant="outlined">Import Cards</v-btn>
            <v-btn @click="exportCollection" class="side_drawer_button" density="comfortable" variant="outlined">Export Collection</v-btn>
            <p v-show="clicks_to_clear >= 1">WARNING: this will delete ALL saved data. You must click the button {{ 10 - clicks_to_clear }} more times to complete the action.</p>
            <v-btn @click="clear_all_data()" class="side_drawer_button" density="comfortable" variant="outlined">Clear ALL card data</v-btn>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </v-card>
  </v-app>
</template>

<script setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'
import { useTheme } from 'vuetify'
import CardSlot from './CardSlot.vue'
import sets_json from './scryfall_data/sets.json'

const theme = useTheme()

var drawer = ref(true)    // signals the set navigation drawer is open
var settings = ref(false) // signals the settings menu is open
var loading = ref(false)  // signals the loading circle is visible
var import_window_active = ref(false) // signals the import dialog is visible
var import_results_active = ref(false) // signals the import dialog results are visible
var export_window_active = ref(false) // signals the import dialog is visible

var import_syntax = ref('moxfield')
var import_text = ''
var import_success = ref(true)
var import_errors = ref([])
var import_card_total = ref(0)
var export_text = ''
var toast = ref(false)

var page_options = reactive({
  show_option_selected: 1,
  full_set_option_selected: 1,
  card_per_page_option_selected: 1
})

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])
var set_search = ref('')
var card_search = ref('')

var collection_stock = reactive({o:{}})  // the user's total card stock, a json object that includes every single card they own (oof?)
// the .o initial object is required to maintain reactivity, because if we overwrite the parent object, we lose reactive()

var rerenderCards = ref(0)
var stats_box_visible = ref(false)

var clicks_to_clear = ref(0)

var current_page = ref(1)
var current_set = ref(null)
var current_set_code = ref('')
var current_set_base_cards = ref(null)
var current_set_commons = ref(0)
var current_set_uncommons = ref(0)
var current_set_rares = ref(0)
var current_set_mythics = ref(0)
var current_set_base_cards_qty = ref(0)
var current_set_extra_cards_qty = ref(0)

var current_set_owned_base_cards = ref(0)
var current_set_owned_commons = ref(0)
var current_set_owned_uncommons = ref(0)
var current_set_owned_rares = ref(0)
var current_set_owned_mythics = ref(0)
var current_set_owned_extra_cards = ref(0)
var current_set_owned_foils = ref(0)

// -------------------------------------------------------------------------------------------------- //

const show_options = [
  {value: 1, title: 'All cards'},
  {value: 2, title: 'Only owned'},
  {value: 3, title: 'Only unowned'}
]
const card_per_page_options = [
  {value: 1, title: 36},
  {value: 2, title: 60},
  {value: 3, title: 120},
  //{value: 4, title: 'All'}
]
const full_set_options = [
  {value: 1, title: 'Every single card, variants included'},
  {value: 2, title: 'Base Set only'},
  {value: 3, title: 'At least one Version of each card name'}
]

// -------------------------------------------------------------------------------------------------- //

onMounted(() => {
  // // localStorage.removeItem('collection_stock')
  set_list.value = sets_json['data']
  
  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  if(set_options)  {  set_types_shown.value = set_options  }
  get_preferences_from_storage()
  
  const local_stock = JSON.parse(localStorage.getItem('collection_stock'))
  if(local_stock) { collection_stock.o = local_stock }

  // delete collection_stock.o['snc']
})

// watch keeps track of variable changes
// whenever collection stock changes, we recalc the total rarities for the current set
watch(collection_stock, new_obj => {
  const cur_set_code = current_set.value?.code
  current_set_owned_commons.value = new_obj.o[cur_set_code]?.commons
  current_set_owned_uncommons.value = new_obj.o[cur_set_code]?.uncommons
  current_set_owned_rares.value = new_obj.o[cur_set_code]?.rares
  current_set_owned_mythics.value = new_obj.o[cur_set_code]?.mythics
  current_set_owned_base_cards.value = new_obj.o[cur_set_code]?.base_set_owned
  current_set_owned_extra_cards.value = new_obj.o[cur_set_code]?.extra_owned
  current_set_owned_foils.value = new_obj.o[cur_set_code]?.foils_owned
  rerenderCards.value++

  localStorage.setItem('collection_stock',JSON.stringify(new_obj.o))
})
// whenever the set options checklist changes, we save it
watch(set_types_shown, new_array => {
  localStorage.setItem('set_options',JSON.stringify(new_array))
})
watch(page_options, v => {
  localStorage.setItem('stored_options',JSON.stringify(page_options))
  current_page.value = 1
})
watch(card_search, v => {
  current_page.value = 1
})

// activated when a set is selected on the left column
// clean up previous values, set up the loading overlay, and grab the new data from the next set
async function select_set(set) 
{
  // console.log("collection stock for selected set",collection_stock.o[set.code])
  loading.value = true

  current_page.value = 1
  card_search.value = ''
  current_set.value = set
  current_set_code.value = set.code

  if(collection_stock.o[set.code] && !collection_stock.o[set.code].foils_owned) {
    collection_stock.o[set.code].foils_owned = tally_foils(set.code)
  }
  
  // for any sets with traditional boosters and structure, we get their base cards and extra cards separately
  if(['core','draft_innovation','masters','expansion','starter'].includes(set.set_type)) {
    current_set_base_cards.value = await get_set_base_cards(set.code)
    current_set_base_cards_qty = current_set_base_cards.value.length
    
    current_set_owned_base_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].base_set_owned : 0
    current_set_owned_commons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].commons : 0
    current_set_owned_uncommons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].uncommons : 0
    current_set_owned_rares.value = collection_stock.o[set.code] ? collection_stock.o[set.code].rares : 0
    current_set_owned_mythics.value = collection_stock.o[set.code] ? collection_stock.o[set.code].mythics : 0
    current_set_owned_extra_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].extra_owned : 0
    current_set_owned_foils.value = collection_stock.o[set.code] ? collection_stock.o[set.code].foils_owned : 0
    
    const extra_set_cards = await get_set_extra_cards(set.code)
    current_set_extra_cards_qty.value = extra_set_cards.length
    current_set_base_cards.value = current_set_base_cards.value.concat( extra_set_cards )
  } else {
    current_set_base_cards.value = await get_set_all_cards(set.code)
    current_set_base_cards_qty = current_set_base_cards.value.length
    current_set_extra_cards_qty.value = 0
    
    current_set_owned_base_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].base_set_owned : 0
    current_set_owned_commons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].commons : 0
    current_set_owned_uncommons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].uncommons : 0
    current_set_owned_rares.value = collection_stock.o[set.code] ? collection_stock.o[set.code].rares : 0
    current_set_owned_mythics.value = collection_stock.o[set.code] ? collection_stock.o[set.code].mythics : 0
    current_set_owned_extra_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].extra_owned : 0
    current_set_owned_foils.value = collection_stock.o[set.code] ? collection_stock.o[set.code].foils_owned : 0
  }

  // sets added via import card may not have this info, so we'll add it in as needed
  if(collection_stock.o[set.code]?.base_set_total == 0) {
    collection_stock.o[set.code].base_set_total = current_set_base_cards_qty
    collection_stock.o[set.code].extra_set_total = current_set_extra_cards_qty ? current_set_extra_cards_qty : 0
  }
  loading.value = false
}

// recovers the user preferences from storage and sets up the screen based on them
function get_preferences_from_storage() {
  // localStorage.clear('stored_options')
  const stored_options = JSON.parse(localStorage.getItem('stored_options'))
  if(stored_options) {
    page_options.full_set_option_selected = stored_options.full_set_option_selected
    page_options.card_per_page_option_selected = stored_options.card_per_page_option_selected
  } else {
    const user_options = {
      full_set_option_selected: {value: 1, title: 'Every single card, variants included'},
      card_per_page_option_selected: {value: 2, title: 60},
    }
    page_options.full_set_option_selected = user_options.full_set_option_selected
    page_options.card_per_page_option_selected = user_options.card_per_page_option_selected

    localStorage.setItem('stored_options',JSON.stringify(page_options))
  }
}

// get all base card information for the selected set
async function get_set_base_cards(set_code) {
  var total_data = []
  var has_more = false
  // var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset&unique=cards&as=grid&order=name"
  var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset+-is%3Aboosterfun+is%3Abooster&unique=cards"
  
  // we will first fetch a scryfall query URL for all unique prints of cards that are on paper and aren't booster fun (showcase, etc)
  // since the scryfall query is limited to 175 results atm and has a 'has_more' field and a query link for the next batch, 
  // we follow down said batches until no has_more and concat the results back
  do {
    const response = await fetch(fetch_url);
    const response_data = await response.json();
    total_data = total_data.concat(response_data['data'])
    has_more = response_data['has_more']
    fetch_url = response_data['next_page']
  } while (has_more != false)

  const set_rarities = get_rarities(total_data)

  current_set_commons.value = set_rarities.common
  current_set_uncommons.value = set_rarities.uncommon
  current_set_rares.value = set_rarities.rare
  current_set_mythics.value = set_rarities.mythic

  return total_data
}

// get all card information for booster fun cards in the selected set
async function get_set_extra_cards(set_code) {
  var total_data = []
  var has_more = false
  var fetch_url = "https://api.scryfall.com/cards/search?order=set&q=set%3A"+set_code+"+%28is%3Apromo+or+is%3Abooster_fun%29+game%3Apaper+unique%3Aprints&unique=cards"
  
  // we will first fetch a scryfall query URL for all unique prints of cards that are on paper and are either booster fun (showcase, etc) or promos (buy a box, bundle, etc)
  // since the scryfall query is limited to 175 results atm and has a 'has_more' field and a query link for the next batch, 
  // we follow down said batches until no has_more and concat the results back
  do {
    const response = await fetch(fetch_url);
    if(response.status === 404){return []}  // extras search can return 404 (no cards), so we just drop the query right there
    const response_data = await response.json();
    total_data = total_data.concat(response_data['data'])
    has_more = response_data['has_more']
    fetch_url = response_data['next_page']
  } while (has_more != false)

  return total_data
}

// get all card information for the selected set
async function get_set_all_cards(set_code) {
  var total_data = []
  var has_more = false
  var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset"
  
  // we will first fetch a scryfall query URL for all unique prints of cards that are on paper
  // since the scryfall query is limited to 175 results atm and has a 'has_more' field and a query link for the next batch, 
  // we follow down said batches until no has_more and concat the results back
  do {
    const response = await fetch(fetch_url);
    const response_data = await response.json();
    total_data = total_data.concat(response_data['data'])
    has_more = response_data['has_more']
    fetch_url = response_data['next_page']
  } while (has_more != false)

  const set_rarities = get_rarities(total_data)

  current_set_commons.value = set_rarities.common
  current_set_uncommons.value = set_rarities.uncommon
  current_set_rares.value = set_rarities.rare
  current_set_mythics.value = set_rarities.mythic

  return total_data
}

// parse and import list of cards on the text box
async function import_cards() {
  loading.value = true
  import_results_active.value = false

  if(import_syntax == 'moxfield') {
    await import_from_moxfield()
  }
  else if(import_syntax == 'native') {
    await import_from_native()
  }
  loading.value = false

  import_results_active.value = true
}

// imports cards with the moxfield syntax
async function import_from_moxfield() {
  let cards_imported = 0
  // first, we split the list of cards imported, one per line
  var split_cards = import_text.split('\n')
  import_text = ''

  var error_list = []
  // then, we iterate through the list
  for(let i = 0; i < split_cards.length; i++) {
    try {
      console.log('split_cards[i]',split_cards[i])
      // for each card, we set up a return object to later use to push the card
      var card = {'name': '', 'amount': 0, 'set': '', 'collector_number': 0, 'foil': false}

      // first we split the card by ' (' (note the space), the first half is the quantity and card name, the second half is the set name, collector number and modifiers
      const card_elements = split_cards[i].split(' (')
      // then we split the first part in two at the first space, and grab the first element as the amount
      const amount = card_elements[0].split(' ',1)[0]
      console.log('amount',amount)
      // if the first element is not a number, it's an error
      if(parseInt(amount)) {
        card.amount = amount
      } else {
        throw EvalError()
      }
      // the remaining elements of the first part should be the card name
      card.name = card_elements[0].substring(card_elements[0].indexOf(' ')+1)
      console.log('card.name',card.name)

      // the second part, past the first parentheses, is further split by the second parentheses; the first element is the set, the second (if exists) may indicate foil
      const second_part = card_elements[1].split(') ')
      console.log('second_part',second_part)
      const third_part = second_part[1]?.split(' ')
      console.log('third_part',third_part)
      card.set = second_part[0].toLowerCase()
      if(parseInt(third_part[0])) {
        card.collector_number = third_part[0]
      } else {
        throw EvalError()
      }
      if(third_part.length >= 2 && ['*F*','*E*'].includes(third_part[1]))
      {
        card.foil = true
        console.log('card.foil = true')
      }

      await add_card_to_stock(card)
      cards_imported++
    }
    catch (e){
      console.log("Error: ",e)
      error_list.push(split_cards[i])
    }
  }
  // we consider the import a success if at least one card was imported
  import_success = (cards_imported > 0)
  import_card_total.value = cards_imported
  import_errors.value = error_list.join(', ')
}

// imports cards using the native json format
async function import_from_native(){

}

function exportCollection () {
  export_text = JSON.stringify(collection_stock.o)
  export_window_active.value = true
}

async function copyCollectionToClipboard() {
  await navigator.clipboard.writeText(export_text);
  toast.value = true
}

// a simplified version of the add_card_to_stock function in CardSlot.vue
async function add_card_to_stock(card) {
  // scryfall fetch for the card, to get the rarity and is_extra info
  var fetch_url = 'https://api.scryfall.com/cards/search?q=%21"'+card.name+'"+set%3A'+card.set+'+%28game%3Apaper%29&unique=prints&order=set'
  const response = await fetch(fetch_url);
  const response_contents = await response.json();
  const response_data = response_contents['data']

  // first, we check if we already have any cards from this set; if not, we create a new empty set with this set's name
  if(!(card.set in collection_stock.o)) {
    var new_set = {
      cards:{},
      commons: 0,
      uncommons: 0,
      rares: 0,
      mythics: 0,
      base_set_owned: 0,
      extra_owned: 0,
      base_set_total: 0,  // both this and below are zeroed due to not enough info at this stage, but we will overwrite it later as needed on CardSlot.vue
      extra_set_total: 0
    }
    collection_stock.o[card.set] = new_set
  }
  
  // next, we check the existing card stock for copies; if yes, we add to the count; if not, we create a new card template for this card
  if(card.name in collection_stock.o[card.set].cards){
    if(card.collector_number in collection_stock.o[card.set].cards[card.name])
    {
      collection_stock.o[card.set].cards[card.name][card.collector_number].count+= parseInt(card.amount)
    }
    else
    {
      collection_stock.o[card.set].cards[card.name][card.collector_number] = {
        count: parseInt(card.amount),
        foil: card.foil
      }
      
      if(card.collector_number == response_data[0].collector_number) {
        collection_stock.o[card.set].base_set_owned++
      } else {
        collection_stock.o[card.set].extra_owned++
      }
    }
  } else {
    console.log('response_data',response_data)
    const new_card = {
      [card.collector_number] : {
        count: parseInt(card.amount),
        foil: card.foil
      }
    }
    collection_stock.o[card.set].cards[card.name] = new_card
    switch(response_data[0].rarity){
      case 'common':
        collection_stock.o[card.set].commons++
        break
      case 'uncommon':
      collection_stock.o[card.set].uncommons++
        break
      case 'rare':
      collection_stock.o[card.set].rares++
        break
      case 'mythic':
      collection_stock.o[card.set].mythics++
        break
      default:
        break
    }
    if(card.collector_number == response_data[0].collector_number) {
      collection_stock.o[card.set].base_set_owned++
    } else {
      collection_stock.o[card.set].extra_owned++
    }
  }
}

// this counts the foils for a set and adds the variable; mostly for backfilling, should be eventually obsolete
function tally_foils(set_code) {
  console.log('Running tally_foils to set missing parameter')
  const data = JSON.parse(JSON.stringify(collection_stock.o[set_code].cards))
  var foiltotal = 0
  const cardlist = Object.entries(data)
  for(let i = 0; i < cardlist.length; i++){
    const elem = Object.entries(cardlist[i][1])
    for(let j = 0; j < elem.length; j++){
      if(elem[j][1]['foil']) {
        foiltotal++
      }
    }
  }
  return foiltotal
}

// removes the collection stock entirely, deleting all data
function clear_all_data() {
  if(clicks_to_clear.value < 9)
  {
    clicks_to_clear.value ++
  }
  else
  {
    clicks_to_clear.value = 0
    collection_stock.o = {}
    localStorage.removeItem('collection_stock')
    location.reload()
  }
}

const getProgressForSet = computed(() => {
  if(collection_stock.o[current_set_code.value])
  {
    switch(page_options.full_set_option_selected.value) {
      case 1:
        // console.log("getProgressForSet, switch 1, value",((collection_stock.o[current_set_code.value].base_set_owned + collection_stock.o[current_set_code.value].extra_owned) / (collection_stock.o[current_set_code.value].base_set_total + collection_stock.o[current_set_code.value].extra_set_total))*100)
        return ((collection_stock.o[current_set_code.value].base_set_owned + collection_stock.o[current_set_code.value].extra_owned) / (collection_stock.o[current_set_code.value].base_set_total + collection_stock.o[current_set_code.value].extra_set_total))*100
      case 2:
        // console.log("getProgressForSet, switch 2, value", (collection_stock.o[current_set_code.value].base_set_owned / collection_stock.o[current_set_code.value].base_set_total)*100)
        return (collection_stock.o[current_set_code.value].base_set_owned / collection_stock.o[current_set_code.value].base_set_total)*100
      case 3:
      // console.log("getProgressForSet, switch 3, value",((collection_stock.o[current_set_code.value].commons + collection_stock.o[current_set_code.value].uncommons + collection_stock.o[current_set_code.value].rares + collection_stock.o[current_set_code.value].mythics) / collection_stock.o[current_set_code.value].base_set_total)*100)
        return ((collection_stock.o[current_set_code.value].commons + collection_stock.o[current_set_code.value].uncommons + collection_stock.o[current_set_code.value].rares + collection_stock.o[current_set_code.value].mythics) / collection_stock.o[current_set_code.value].base_set_total)*100
      default:
        console.log("Something very wrong happened with page_options.full_set_option_selected on render")
        return 0
    }
  } else {return 0}
})
const pageCount = computed(() => {
  const total_cards_to_display = current_set_base_cards.value.filter((card) => (card.name.toLowerCase().includes(card_search.value) || card_search.value == '')).length
  return (page_options && page_options.card_per_page_option_selected && (page_options.card_per_page_option_selected.value != 4)) 
    ? Math.ceil(total_cards_to_display / page_options.card_per_page_option_selected.title) : 0
})
const pageSliceStart = computed(() => {
  return 0 + (page_options.card_per_page_option_selected.value != 4 ? (current_page.value-1)* page_options.card_per_page_option_selected.title : 0)
})
const pageSliceEnd = computed(() => {
  return (page_options.card_per_page_option_selected.value != 4 ? Math.min(current_set_base_cards.value.length, current_page.value * page_options.card_per_page_option_selected.title) : current_set_base_cards.value.length)
})

// returns object with the distinct rarities of passed set
function get_rarities(set) {
  var cards_checked = []
  var rarities = {'common':0, 'uncommon':0, 'rare': 0, 'mythic':0 }
  for(let i = 0; i < set.length; i++) {
    if(!cards_checked.includes(set[i].name))
    {
      cards_checked.push(set[i].name)
      switch(set[i].rarity)
      {
        case 'common':
          rarities.common++
          break
        case 'uncommon':
          rarities.uncommon++
          break
        case 'rare':
          rarities.rare++
          break
        case 'mythic':
          rarities.mythic++
          break
        default:
          break
      }
    }
  }
  return rarities
}

function on_scroll_stats_box () {
  stats_box_visible.value = window.scrollY > 280
}

</script>

<style scoped>
.page_title_bar {
  background-color: ffffff;
}
.column_header {
  font-weight: bold; 
  text-align: left;
  padding-left: 20px;
}
.v-list-item {
  padding: 0 16px !important;
  margin: 0 !important;
  min-height: 0 !important;  
}
.set_page_title_card {
  height: 100px;
}
.set_page_title {
  font-weight: bold;
  font-size: 20pt;
  font-family: Georgia, 'Times New Roman', Times, serif;
}
.set_page_subtitle {
  font-weight: bold;
  font-size: 10pt;
  font-family: Georgia, 'Times New Roman', Times, serif;
}
.set_page_subtext {
  font-size: 10pt;
  font-family: Georgia, 'Times New Roman', Times, serif;
}
.set_list_element {
  display: flex;
  width: 100%;
  max-height: 25px;
}
.set_list_element:hover {
  cursor:pointer;
  background-color: rgb(255, 221, 231);
}
.set_list_element_selected {
  background-color: rgb(255, 162, 190);
  font-weight: bold;
}
.set_logo, .set_check {
  display: inline-block;
  margin-right: 5px;
  accent-color: rgb(255, 162, 190);
}
.set_list_name {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}
.main_body {
  width: 60%;
  max-width: 1400px;
  display: inline-block;
  text-align: center;
}
.v-col {
  padding: 0;
}
.set_stats_box {
  width: 200px;
  height: 225px;
  border-radius: 5%;
  display: block;
  float:right;
  position: fixed;
  top: 20%;
  right: 50px;
}
.set_stats_inner_box {
  width: 200px;
  height: 210px;
  border-radius: 5%;
  display: inline-block;
  padding: 15px;
  margin-top:-6px;
}
.page_header {
  height: 105px;
  margin-bottom: 10px;
}
.set_stats_banner {
  width: 100%;
  height: 90px;
  display: block;
  padding: 15px;
}
.side_drawer_button {
  margin-top: 10px;
  margin-bottom: 10px;
}
.side_drawer_button:hover {
  background-color: #F8BBD0;
}
.import_window {
  width: 500px;
  height: 330px;
  text-align: center;
}
.import_results_window {
  width: 450px;
  min-height: 250px;
  max-height: 600px;
  height: 100%;
  text-align: center;
}
.import_window_header {
  width: 100%;
  height: 70px;
}
.import_text_field {
  width: 450px;
  height: 150px;
  display: inline-block;
  margin-top: 10px;
}
.page_footer {
  width: 100% !important;
  height: 400px;
  bottom: 0;
}
@media screen and (max-width: 1350px) {
  .set_stats_box {
    display: none;
  }
}
@media screen and (min-width: 1530px) {
  .main_body {
    width: 900px;
  }
}
@media screen and (max-width: 1529px) {
  .main_body {
    width: 80%;
  }
}
@media screen and (max-width: 960px) {
  .main_body {
    width: 95%;
  }
}
</style>
