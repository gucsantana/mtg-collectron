<template>
  <div name="main">
    <div class="left-column" :key="render_key_column">
      <p id="column_set_visib_title" class="column_header">Set Visibility</p>
      <div style="display: inline-block;">
        <input type="checkbox" id="check_core" value="core" v-model="set_types_shown" class="set_check" :checked="check_core">
          <label for="check_core" style="display: inline-block;">Core Sets</label>
      </div>
      <div style="display: inline-block;">
        <input type="checkbox" value="expansion" v-model="set_types_shown" class="set_check" :checked="check_expansion">
          <p style="display: inline-block;">Expansions</p>
      </div>
      <div style="display: inline-block;">
        <input type="checkbox" value="masters" v-model="set_types_shown" class="set_check" :checked="check_masters">
          <p style="display: inline-block;">Masters Sets</p>
      </div>
      <p id="column_set_list_title" class="column_header">List of Sets</p>
      <div v-for="set in set_list"> <div :id="set['code']" v-show="set['digital'] == false && set_types_shown.includes(set['set_type'])" class="set_list_element" @click="select_set(set)">
        <!-- <img :src="set['icon_svg_uri']" class="set_logo" width="18px" height="18px"/> -->
        <p class="set_list_name">{{ set['name'] }}</p>
      </div> </div>
    </div>
    <div class="set_stats_box" v-if="current_set && current_set_booster_cards" :key="render_key_stats_box">
      <p>Base Cards: 0/{{ current_set_booster_cards.length }}</p>
      <p v-if="current_set_commons > 0">Commons: 0/{{ current_set_commons }}</p>
      <p v-if="current_set_uncommons > 0">Uncommons: 0/{{ current_set_uncommons }}</p>
      <p v-if="current_set_rares > 0">Rares: 0/{{ current_set_rares }}</p>
      <p v-if="current_set_mythics > 0">Mythic Rares: 0/{{ current_set_mythics }}</p>
      <p v-if="current_set['card_count'] - current_set_booster_cards.length > 0">Booster Fun Cards: 0/{{ current_set['card_count'] - current_set_booster_cards.length }}</p>
      <p>Grand Total Cards: 0/{{ current_set['card_count'] }}</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import sets_json from './scryfall_data/sets.json'

var render_key_column = 0
var render_key_stats_box = 0

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])

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
  console.log(sets_json['data'])

  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  console.log("loaded set options",JSON.stringify(set_options))
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

  console.log('total data for set',total_data)
  return total_data
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
}
.column_header {
  font-weight: bold;
  text-align: left;
  padding-left: 20px;
}
.set_list_element {
  display: flex;
  width: 180px;
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
.set_stats_box {
  width: 200px;
  height: 200px;
  background-color: aliceblue;
  display: block;
  float:right;
  position: fixed;
  top: 20%;
  right: 50px;
}
</style>
