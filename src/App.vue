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
        <p class="set_page_title" v-if="current_set && current_set_base_cards">{{ current_set['name'] }}</p>
        <v-card class="set_stats_banner" v-if="current_set && current_set_base_cards">
          <v-row style="height: 80px;" align="center" >
            <v-col><p>Base Set:</p><p>{{ current_set_owned_base_cards }}/{{ current_set_base_cards.length }}</p></v-col>
            <v-divider vertical/>
            <v-col v-if="current_set_commons > 0"><p>Commons:</p><p>{{ current_set_owned_commons }}/{{ current_set_commons }}</p></v-col>
            <v-divider vertical v-if="current_set_commons > 0"/>
            <v-col v-if="current_set_uncommons > 0"><p>Uncommons:</p><p>{{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p></v-col>
            <v-divider vertical v-if="current_set_uncommons > 0"/>
            <v-col v-if="current_set_rares > 0"><p>Rares:</p><p>{{ current_set_owned_rares }}/{{ current_set_rares }}</p></v-col>
            <v-divider vertical v-if="current_set_rares > 0"/>
            <v-col v-if="current_set_mythics > 0"><p>Mythic Rares:</p><p>{{ current_set_owned_mythics }}/{{ current_set_mythics }}</p></v-col>
            <v-divider vertical v-if="current_set_mythics > 0"/>
            <v-col v-if="current_set_boosterfun_cards"><p>Booster Fun:</p><p>{{ current_set_owned_boosterfun_cards }}/{{ current_set_boosterfun_cards.length }}</p></v-col>
            <v-divider vertical v-if="current_set_boosterfun_cards"/>
            <v-col><p>Grand Total:</p><p>{{ current_set_owned_base_cards + current_set_owned_boosterfun_cards }}/{{ current_set['card_count'] }}</p></v-col>
          </v-row>
        </v-card>
        <v-sheet name="normal_cards_holder">
          <v-row no-gutters>
            <v-col v-for="card in current_set_base_cards" cols="6" sm="6" md="4" lg="3">
              <CardSlot :card="card" :collection_stock="collection_stock" :current_set_code="current_set_code" :is_booster_fun="false"></CardSlot>
            </v-col>
          </v-row>
        </v-sheet>
        <v-sheet name="booster_fun_cards_holder">
          <v-row no-gutters>
            <v-col v-for="card in current_set_boosterfun_cards" cols="6" sm="6" md="4" lg="3">
              <CardSlot :card="card" :collection_stock="collection_stock" :current_set_code="current_set_code" :is_booster_fun="true"></CardSlot>
            </v-col>
          </v-row>
        </v-sheet>
      </v-sheet>
      <v-card class="set_stats_box" v-if="current_set && current_set_base_cards" :key="render_key_stats_box" :elevation="10">
        <p>Base Set: {{ current_set_owned_base_cards }}/{{ current_set_base_cards.length }}</p>
        <p v-if="current_set_commons > 0">Commons: {{ current_set_owned_commons }}/{{ current_set_commons }}</p>
        <p v-if="current_set_uncommons > 0">Uncommons: {{ current_set_owned_uncommons }}/{{ current_set_uncommons }}</p>
        <p v-if="current_set_rares > 0">Rares: {{ current_set_owned_rares }}/{{ current_set_rares }}</p>
        <p v-if="current_set_mythics > 0">Mythic Rares: {{ current_set_owned_mythics }}/{{ current_set_mythics }}</p>
        <p v-if="current_set_boosterfun_cards">Booster Fun: {{ current_set_owned_boosterfun_cards }}/{{ current_set_boosterfun_cards.length }}</p>
        <p>Grand Total: {{ current_set_owned_base_cards + current_set_owned_boosterfun_cards }}/{{ current_set['card_count'] }}</p>
      </v-card>
    </v-main>
  </v-app>
</template>

<script setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'
import CardSlot from './CardSlot.vue'
import sets_json from './scryfall_data/sets.json'

var render_key_column = 0
var render_key_stats_box = 0

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])

var collection_stock = reactive({})  // the user's total card stock, a json object that includes every single card they own (oof?)

var check_core = false
var check_expansion = false
var check_masters = false

var current_set = ref(null)
var current_set_code = ref('')
var current_set_base_cards = ref(null)
var current_set_boosterfun_cards = ref(null)
var current_set_owned_base_cards = ref(0)
var current_set_owned_boosterfun_cards = ref(0)
var current_set_commons = ref(0)
var current_set_uncommons = ref(0)
var current_set_rares = ref(0)
var current_set_mythics = ref(0)

var current_set_owned_commons = ref(0)
var current_set_owned_uncommons = ref(0)
var current_set_owned_rares = ref(0)
var current_set_owned_mythics = ref(0)

onMounted(() => {
  set_list.value = sets_json['data']

  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  if(set_options)  {  set_types_shown.value = set_options  }
})

// watch keeps track of variable changes
// whenever collection stock changes, we recalc the total rarities for the current set
watch(collection_stock, new_obj => {
  const cur_set_code = current_set.value?.code
  current_set_owned_commons.value = new_obj[cur_set_code]?.commons
  current_set_owned_uncommons.value = new_obj[cur_set_code]?.uncommons
  current_set_owned_rares.value = new_obj[cur_set_code]?.rares
  current_set_owned_mythics.value = new_obj[cur_set_code]?.mythics
  current_set_owned_base_cards.value = new_obj[cur_set_code]?.base_set
  current_set_owned_boosterfun_cards.value = new_obj[cur_set_code]?.booster_fun
})
// whenever the set options checklist changes, we save it
watch(set_types_shown, new_array => {
  localStorage.setItem('set_options',JSON.stringify(new_array))
})

// activated when a set is selected on the left column
async function select_set(set) 
{
  current_set.value = set
  current_set_code.value = set.code
  current_set_base_cards.value = await get_set_cards(set.code)
  current_set_boosterfun_cards.value = await get_set_boosterfun_cards(set.code)
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

// get all card information for booster fun cards in the selected set
async function get_set_boosterfun_cards(set_code) {
  var total_data = []
  var has_more = false
  var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset+is%3Aboosterfun&unique=cards&as=grid&order=name"
  
  // we will first fetch a scryfall query URL for all unique prints of cards that are on paper and are booster fun (showcase, etc)
  // since the scryfall query is limited to 175 results atm and has a 'has_more' field and a query link for the next batch, 
  // we follow down said batches until no has_more and concat the results back
  do {
    const response = await fetch(fetch_url);
    if(response.status === 404){return []}  // booster fun search can return 404 (no cards), so we just drop the query right there
    const response_data = await response.json();
    total_data = total_data.concat(response_data['data'])
    has_more = response_data['has_more']
    fetch_url = response_data['next_page']
  } while (has_more != false)

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
.set_page_title {
  font-weight: bold;
  font-size: 20pt;
  font-family: Georgia, 'Times New Roman', Times, serif;
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
