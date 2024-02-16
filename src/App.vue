<template>
  <v-app>
    <v-main name="main" style="display: flex;">
      <v-navigation-drawer class="left-column" :key="render_key_column" :width="200" :permanent=true>
        <v-list-item id="column_set_visib_title"><p class="column_header">Set Visibility</p></v-list-item>
        <v-list-item style="display: inline-block; width:100%;">
          <input type="checkbox" id="check_core" value="core" v-model="set_types_shown" class="set_check" :checked="check_core">
            <label for="check_core" style="display: inline-block;">Core Sets</label>
        </v-list-item>
        <v-list-item style="display: inline-block; width:100%;">
          <input type="checkbox" value="expansion" v-model="set_types_shown" class="set_check" :checked="check_expansion">
            <p style="display: inline-block;">Expansions</p>
        </v-list-item>
        <v-list-item style="display: inline-block; width:100%;">
          <input type="checkbox" value="masters" v-model="set_types_shown" class="set_check" :checked="check_masters">
            <p style="display: inline-block;">Masters Sets</p>
        </v-list-item>
        <v-list-item id="column_set_list_title"><p class="column_header">List of Sets</p></v-list-item>
        <v-list-item v-for="set in set_list"> <div :id="set['code']" v-show="set['digital'] == false && set_types_shown.includes(set['set_type'])" class="set_list_element" @click="select_set(set)">
          <!-- <img :src="set['icon_svg_uri']" class="set_logo" width="18px" height="18px"/> -->
          <p class="set_list_name">{{ set['name'] }}</p>
        </div> </v-list-item>
      </v-navigation-drawer>
      <v-sheet class="main_body">
        <v-card class="set_stats_banner" v-if="current_set && current_set_booster_cards" :key="render_key_stats_box">
          <v-row style="height: 80px;" align="center" >
            <v-col><p>Base Set:</p><p>0/{{ current_set_booster_cards.length }}</p></v-col>
            <v-divider vertical/>
            <v-col v-if="current_set_commons > 0"><p>Commons:</p><p>0/{{ current_set_commons }}</p></v-col>
            <v-divider vertical v-if="current_set_commons > 0"/>
            <v-col v-if="current_set_uncommons > 0"><p>Uncommons:</p><p>0/{{ current_set_uncommons }}</p></v-col>
            <v-divider vertical v-if="current_set_uncommons > 0"/>
            <v-col v-if="current_set_rares > 0"><p>Rares:</p><p>0/{{ current_set_rares }}</p></v-col>
            <v-divider vertical v-if="current_set_rares > 0"/>
            <v-col v-if="current_set_mythics > 0"><p>Mythic Rares:</p><p>0/{{ current_set_mythics }}</p></v-col>
            <v-divider vertical v-if="current_set_mythics > 0"/>
            <v-col v-if="current_set['card_count'] - current_set_booster_cards.length > 0"><p>Booster Fun:</p><p>0/{{ current_set['card_count'] - current_set_booster_cards.length }}</p></v-col>
            <v-divider vertical v-if="current_set['card_count'] - current_set_booster_cards.length > 0"/>
            <v-col><p>Grand Total:</p><p>0/{{ current_set['card_count'] }}</p></v-col>
          </v-row>
        </v-card>
        <v-sheet class="card_holder">
          <v-row no-gutters>
            <v-col class="card_element" v-for="card in current_set_booster_cards" cols="6" sm="6" md="4" lg="3">
              <v-hover v-slot="{ isHovering, props }">
                <v-card :class="{ 'on-hover': isHovering }" :="props" :card-data="card">
                  <img :src="getCardImage(card['image_uris'],card['card_faces'])" class="card_image" :class="{ 'lit_up_card_image': isHovering }">
                  <v-btn @click="add_card_to_stock(card)" class="add_card_button" v-show="isHovering" density="comfortable" ><v-icon icon="mdi-plus" size="x-large" color="teal-accent-3"/></v-btn>
                </v-card>
              </v-hover>
            </v-col>
          </v-row>
        </v-sheet>
      </v-sheet>
      <v-card class="set_stats_box" v-if="current_set && current_set_booster_cards" :key="render_key_stats_box" :elevation="10">
        <p>Base Set: 0/{{ current_set_booster_cards.length }}</p>
        <p v-if="current_set_commons > 0">Commons: 0/{{ current_set_commons }}</p>
        <p v-if="current_set_uncommons > 0">Uncommons: 0/{{ current_set_uncommons }}</p>
        <p v-if="current_set_rares > 0">Rares: 0/{{ current_set_rares }}</p>
        <p v-if="current_set_mythics > 0">Mythic Rares: 0/{{ current_set_mythics }}</p>
        <p v-if="current_set['card_count'] - current_set_booster_cards.length > 0">Booster Fun: 0/{{ current_set['card_count'] - current_set_booster_cards.length }}</p>
        <p>Grand Total: 0/{{ current_set['card_count'] }}</p>
      </v-card>
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import sets_json from './scryfall_data/sets.json'

var render_key_column = 0
var render_key_stats_box = 0

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])

var collection_stock = ref({})  // the user's total card stock, a json object that includes every single card they own (oof?)

var check_core = false
var check_expansion = false
var check_masters = false

var current_set = ref(null)
var current_set_booster_cards = ref(null)
var current_set_commons = ref(0)
var current_set_uncommons = ref(0)
var current_set_rares = ref(0)
var current_set_mythics = ref(0)

onMounted(() => {
  set_list.value = sets_json['data']

  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  if(set_options)  {  set_types_shown.value = set_options  }
})

// watch keeps track of variable changes
watch(set_types_shown, new_array => {
  localStorage.setItem('set_options',JSON.stringify(new_array))
  forceRerenderColumn()
})

// activated when a set is selected on the left column
async function select_set(set) 
{
  current_set.value = set
  current_set_booster_cards.value = await get_set_cards(set['code'])
  forceRerenderStatsBox()
}

// get all card information for the selected set
async function get_set_cards(set_code) {
  var total_data = []
  var has_more = false
  var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset+-is%3Aboosterfun+is%3Abooster&unique=cards&as=grid&order=name"
  
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

// passing the card images uri array and possible card faces object, return an image uri, prioritizing images uri
function getCardImage(uriArray,cardFacesArray){
  if(uriArray)
  {
    return uriArray['normal']
  }
  else if(cardFacesArray)
  {
    return cardFacesArray[0]['image_uris']['normal']
  }
  else return
}

function add_card_to_stock(card_data){
  var set_stock = {}

  // first, we check if we already have any cards from this set; if yes, we grab the existing data; if not, we create a new empty set with this set's name
  if(card_data['set'] in this.collection_stock) {
    set_stock = this.collection_stock[card_data['set']]
  } else {
    var new_set = {
      cards:[],
      commons: 0,
      uncommons: 0,
      rares: 0,
      mythics: 0,
      booster_fun: 0
    }
    this.collection_stock.push({ [card_data['set']] : new_set})
    set_stock = this.collection_stock[card_data['set']]
  }
  console.log(set_stock)
  return
  // next, we check the existing card stock for copies; if yes, we add to the count; if not, we create a new card template for this card
  if(card_data['name'] in set_stock){
    var card_stock = set_stock[card_data['name']]
    card_stock['count'] ++
  } else {
    var new_card = {
      count: 1,
      rarity: card_data['rarity'],
      foil: false
    }
    set_stock['cards'].push(new_card)
    switch(card_data){
      case 'common':
        set_stock['commons']++
        break
      case 'uncommon':
        set_stock['uncommons']++
        break
      case 'rare':
        set_stock['rares']++
        break
      case 'mythic':
        set_stock['mythics']++
        break
      default:
        break
    }
  }
  console.log("current card stock",this.collection_stock.value)
}

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

function forceRerenderColumn()
{
  render_key_column += 1
}
function forceRerenderStatsBox()
{
  render_key_stats_box += 1
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
  padding: 0 16px;
  min-height: 0;  
}
.set_list_element {
  display: flex;
  width: 160px;
  max-height: 25px;
}
.set_list_element:hover {
  cursor:pointer;
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
.card_element {
  display: inline-block;
  position: relative;
}
.card_image {
  width: 100%; 
  -webkit-filter: grayscale(1);
  filter: grayscale(1);
}
.lit_up_card_image {
  -webkit-filter: grayscale(0);
  filter: grayscale(0);
}
.add_card_button {
  display:inline-block;
  position:absolute;
  top: 10px;
  right: 10px;
  background-color: rgb(232, 253, 246);
}
.rainbow-box {
  border: 5px solid transparent;
  border-image: linear-gradient(to bottom right, #b827fc 0%, #2c90fc 25%, #b8fd33 50%, #fec837 75%, #fd1892 100%);
  border-image-slice: 1;
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
.set_stats_banner {
  width: 100%;
  height: 80px;
  display: block;
  padding: 15px;
  margin-bottom: 10px;
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
