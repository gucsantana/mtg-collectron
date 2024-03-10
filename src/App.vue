<template>
  <v-app>
    <v-overlay :model-value="loading" class="align-center justify-center">
      <v-progress-circular color="primary" indeterminate size="64"/>
    </v-overlay>
    <v-overlay persistent :model-value="import_window_active" class="align-center justify-center">
      <v-card title="Import Cards" class="import_window">
        <v-textarea class="import_text_field" variant="outlined"/>
        <v-row>
          <v-spacer/>
          <v-col cols="3"><v-btn>Import</v-btn></v-col>
          <v-col cols="3"><v-btn @click="import_window_active=false">Close</v-btn></v-col>
        </v-row>
      </v-card>
    </v-overlay>
    <v-app-bar>
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
            <input type="checkbox" value="masterpiece" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Masterpieces</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="all" v-model="set_types_shown" class="set_check">
              <p style="display: inline-block;">Other Sets</p>
          </v-list-item>
        </v-list>
        <v-list-item id="column_set_list_title"><p class="column_header">List of Sets</p></v-list-item>
        <v-list-item v-for="set in set_list"> <div @click="select_set(set)" v-show="set['digital'] == false && (set_types_shown.includes(set['set_type']) || (set_types_shown.includes('all') && !['core','expansion','commander','masters','masterpiece'].includes(set['set_type'])))" class="set_list_element" :class="{'set_list_element_selected': set['code'] == current_set_code }" >
          <!-- <img :src="set['icon_svg_uri']" class="set_logo" width="18px" height="18px"/> -->
          <p class="set_list_name">{{ set['name'] }}</p>
        </div> </v-list-item>
      </v-navigation-drawer>
    </v-card>
    <v-main name="main" v-if="current_set && current_set_base_cards">
      <v-sheet class="main_body">
        <v-card class="set_page_title_card" flat>
          <div>
            <p class="set_page_title">{{ current_set['name'] }}</p>
          </div>
          <div style="display:inline-block">
            <p class="set_page_subtitle">Release Date:</p><p class="set_page_subtext">{{ current_set['released_at'] }}</p>
          </div>
          <div style="display:inline-block">
            <p class="set_page_subtitle">Set Type:</p><p class="set_page_subtext">{{ current_set['set_type'] }}</p>
          </div>
        </v-card>
        <v-row>
          <v-spacer/>
          <v-col cols="3">
            <v-select v-model="page_options.card_per_page_option_selected" label="Cards per Page:" :items="card_per_page_options" return-object density="compact"/>
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
              <v-col v-if="current_set_commons > 0"><p>Commons:</p><p>{{ current_set_owned_commons }}/{{ current_set_commons }}</p></v-col>
              <v-divider vertical v-if="current_set_commons > 0"/>
              <v-col v-if="current_set_uncommons > 0"><p>Uncommons:</p><p>{{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p></v-col>
              <v-divider vertical v-if="current_set_uncommons > 0"/>
                <v-col v-if="current_set_rares > 0"><p>Rares:</p><p>{{ current_set_owned_rares }}/{{ current_set_rares }}</p></v-col>
                <v-divider vertical v-if="current_set_rares > 0"/>
              <v-col v-if="current_set_mythics > 0"><p>Mythic Rares:</p><p>{{ current_set_owned_mythics }}/{{ current_set_mythics }}</p></v-col>
              <v-divider vertical v-if="current_set_mythics > 0"/>
              <v-col v-if="current_set_extra_cards_qty > 0"><p>Extra Cards:</p><p>{{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p></v-col>
              <v-divider vertical v-if="current_set_extra_cards_qty > 0"/>
              <v-col><p>Grand Total:</p><p>{{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p></v-col>
            </v-row>
          </v-card>
          <v-progress-linear height="15" v-model="getProgressForSet" :color="getProgressForSet < 100 ? 'pink-lighten-1' : 'amber-lighten-2' "/>
        </v-card>
        <v-sheet name="normal_cards_holder">
          <v-row no-gutters>
            <v-col v-for="(item,index) in current_set_base_cards.slice(pageSliceStart,pageSliceEnd)" cols="6" sm="6" md="4" lg="3" >
              <CardSlot :card="item" :collection_stock="collection_stock.o" :current_set_code="current_set_code" :show_option="page_options.show_option_selected.value" :is_extra="(index+pageSliceStart) >= current_set_base_cards_qty" :base_set_total="current_set_base_cards_qty" :extra_set_total="current_set_extra_cards_qty"></CardSlot>
            </v-col>
          </v-row>
        </v-sheet>
      </v-sheet>
      <v-pagination v-if="page_options.card_per_page_option_selected != 4" v-model="current_page" :length="pageCount" total-visible="8"/>
      <v-card class="set_stats_box" :elevation="10">
        <p>Base Set: {{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p>
        <p v-if="current_set_commons > 0">Commons: {{ current_set_owned_commons }}/{{ current_set_commons }}</p>
        <p v-if="current_set_uncommons > 0">Uncommons: {{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p>
        <p v-if="current_set_rares > 0">Rares: {{ current_set_owned_rares }}/{{ current_set_rares }}</p>
        <p v-if="current_set_mythics > 0">Mythic Rares: {{ current_set_owned_mythics }}/{{ current_set_mythics }}</p>
        <p v-if="current_set_extra_cards_qty > 0">Extra Cards: {{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p>
        <p>Grand Total: {{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p>
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
            <p v-show="clicks_to_clear >= 1">WARNING: this will delete ALL saved data. You must click the button {{ 10 - clicks_to_clear }} more times to complete the action.</p>
            <v-btn @click="clear_all_data()" class="side_drawer_button" density="comfortable" variant="outlined">Clear ALL card data</v-btn>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </v-card>
    <!-- <v-footer></v-footer> -->
  </v-app>
</template>

<script setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'
import { useTheme } from 'vuetify'
import CardSlot from './CardSlot.vue'
import sets_json from './scryfall_data/sets.json'

var drawer = ref(true)    // signals the set navigation drawer is open
var settings = ref(false) // signals the settings menu is open
var loading = ref(false)  // 
var import_window_active = ref(false) // signals the import dialog is visible

var page_options = reactive({
  show_option_selected: 1,
  full_set_option_selected: 1,
  card_per_page_option_selected: 1
})

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])

var collection_stock = reactive({o:{}})  // the user's total card stock, a json object that includes every single card they own (oof?)
// the .o initial object is required to maintain reactivity, because if we overwrite the parent object, we lose reactive()

var rerenderCards = ref(0)

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
  {value: 4, title: 'All'}
]
const full_set_options = [
  {value: 1, title: 'Every single card, variants included'},
  {value: 2, title: 'Base Set only'},
  {value: 3, title: 'At least one Version of each card name'}
]

// -------------------------------------------------------------------------------------------------- //

onMounted(() => {
  // localStorage.removeItem('collection_stock')
  set_list.value = sets_json['data']

  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  if(set_options)  {  set_types_shown.value = set_options  }
  get_preferences_from_storage()
  
  const local_stock = JSON.parse(localStorage.getItem('collection_stock'))
  if(local_stock) { collection_stock.o = local_stock }
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

// activated when a set is selected on the left column
// clean up previous values, set up the loading overlay, and grab the new data from the next set
async function select_set(set) 
{
  loading.value = true

  current_page.value = 1
  current_set.value = set
  current_set_code.value = set.code
  
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

    const extra_set_cards = await get_set_extra_cards(set.code)
    current_set_extra_cards_qty.value = extra_set_cards.length
    current_set_base_cards.value = current_set_base_cards.value.concat( extra_set_cards )
  } else {
    current_set_base_cards.value = await get_set_all_cards(set.code)
    current_set_base_cards_qty = current_set_base_cards.value.length

    current_set_owned_base_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].base_set_owned : 0
    current_set_owned_commons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].commons : 0
    current_set_owned_uncommons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].uncommons : 0
    current_set_owned_rares.value = collection_stock.o[set.code] ? collection_stock.o[set.code].rares : 0
    current_set_owned_mythics.value = collection_stock.o[set.code] ? collection_stock.o[set.code].mythics : 0
    current_set_owned_extra_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].extra_owned : 0
  }
  loading.value = false
}

// recovers the user preferences from storage and sets up the screen based on them
function get_preferences_from_storage() {
  // localStorage.clear('stored_options')
  const stored_options = JSON.parse(localStorage.getItem('stored_options'))
  if(stored_options) {
    page_options.show_option_selected = stored_options.show_option_selected
    page_options.full_set_option_selected = stored_options.full_set_option_selected
    page_options.card_per_page_option_selected = stored_options.card_per_page_option_selected
  } else {
    const user_options = {
      show_option_selected: 1,
      full_set_option_selected: 1,
      card_per_page_option_selected: 2,
    }
    page_options.show_option_selected = user_options.show_option_selected
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

  current_set_commons.value = total_data.filter(is_common).length
  current_set_uncommons.value = total_data.filter(is_uncommon).length
  current_set_rares.value = total_data.filter(is_rare).length
  current_set_mythics.value = total_data.filter(is_mythic).length

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

  current_set_commons.value = total_data.filter(is_common).length
  current_set_uncommons.value = total_data.filter(is_uncommon).length
  current_set_rares.value = total_data.filter(is_rare).length
  current_set_mythics.value = total_data.filter(is_mythic).length

  return total_data
}

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
  const total_cards_to_display = current_set_base_cards.value ? current_set_base_cards.value.length : 0
  return (page_options && page_options.card_per_page_option_selected && (page_options.card_per_page_option_selected.value != 4)) 
    ? Math.ceil(total_cards_to_display / page_options.card_per_page_option_selected.title) : 0
})
const pageSliceStart = computed(() => {
  return 0 + (page_options.card_per_page_option_selected.value != 4 ? (current_page.value-1)* page_options.card_per_page_option_selected.title : 0)
})
const pageSliceEnd = computed(() => {
  return (page_options.card_per_page_option_selected.value != 4 ? Math.min(current_set_base_cards.value.length, current_page.value * page_options.card_per_page_option_selected.title) : current_set_base_cards.value.length)
})

// aux functions for checking rarity
function is_common(card){
  return card['rarity'] == 'common'
}
function is_uncommon(card){
  return card['rarity'] == 'uncommon'
}
function is_rare(card){
  return card['rarity'] == 'rare'
}
function is_mythic(card){
  return card['rarity'] == 'mythic'
}

</script>

<style scoped>
.left-column {
  width: 180px;
  display: inline-block;
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
}
.set_list_name {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}
.main_body {
  /* background-color: aquamarine; */
  width: 60%;
  max-width: 1400px;
  display: inline-block;
  /* margin-top: 50px; */
  text-align: center;
}
.v-col {
  padding: 0;
}
.set_stats_box {
  width: 200px;
  height: 200px;
  border-radius: 5%;
  display: block;
  float:right;
  position: fixed;
  top: 20%;
  right: 50px;
  padding: 15px;
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
.import_window {
  width: 500px;
  height: 300px;
  text-align: center;
}
.import_text_field {
  width: 450px;
  height: 150px;
  display: inline-block;
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
