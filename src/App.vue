<template>
  <div name="main">
    <div class="left-column">
      <p id="column_set_title" class="column_header">Sets</p>
      <div v-for="set in set_list"> <div v-if="set['digital'] == false && set_types_shown.includes(set['set_type'])" class="set_list_element">
        <img :src="set['icon_svg_uri']" class="set_logo" width="18px" height="18px"/>
        <p class="set_list_name">{{ set['name'] }}</p>
      </div> </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import sets_json from './scryfall_data/sets.json'

var set_list = ref([])
var set_types_shown = ref(['core','expansion'])

onMounted(() => {
  set_list.value = sets_json['data']
  console.log(sets_json['data'])
})
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
.set_logo {
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
</style>
