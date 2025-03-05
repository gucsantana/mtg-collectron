<!-- This component represents a single card being rendered on the screen and all the associated buttons and thingamajigs -->
<template>
    <v-hover v-slot="{ isHovering, props }" v-if="isCardVisible">
        <v-card :class="{ 'on-hover': isHovering, 'card-element': true }" :="props" flat>
          <img :src="getCardImage(card['image_uris'],card['card_faces'])" class="card_image" :class="{ 'lit_up_card_image': isHovering, 'card_owned': isCardOwned}">
          <v-card name="foil_overlay" :class="{'foil_card_frame':isCardFoil}"></v-card>
          <v-btn @click="add_card_to_stock(card)" class="main_add_card_button" v-show="isHovering" v-if="!isCardOwned" density="comfortable" >
            <v-icon icon="mdi-plus-thick" size="x-large" color="teal-accent-3"/>
          </v-btn>
          <v-btn @click="mark_card_as_foil(card)" class="btn_foil_modify" v-show="isHovering" v-if="isCardOwned && !isCardFoil" color="purple-lighten-3" density="comfortable">
            <v-icon icon="mdi-star-outline" size="x-large" color="white"/>
            <v-tooltip activator="parent" location="bottom">Set as Foil</v-tooltip>
          </v-btn>
          <v-btn @click="mark_card_as_nonfoil(card)" class="btn_foil_modify" v-show="isHovering" v-if="isCardOwned && isCardFoil" color="purple-lighten-3" density="comfortable">
            <v-icon icon="mdi-star" size="x-large" color="white"/>
            <v-tooltip activator="parent" location="bottom">Remove Foil</v-tooltip>
          </v-btn>
          <v-card v-show="isHovering" v-if="isCardOwned" class="owned_card_controls">
            <v-row no-gutters align="center">
              <v-col cols="4" class="sub_remove_card_btn" @click="remove_card_from_stock(card)"><v-icon icon="mdi-minus-thick" size="large" color="red-lighten-5"/></v-col>
              <v-col cols="4" class="sub_card_count"><p class="card_count">{{ this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].count }}</p></v-col>
              <v-col cols="4" class="sub_add_card_btn" @click="add_card_to_stock(card)"><v-icon icon="mdi-plus-thick" size="large" color="teal-lighten-5"/></v-col>
            </v-row>
          </v-card>
          <v-card v-show="isHovering" v-if="isCardOwned" class="tag_card_controls">
            <v-row no-gutters align="center">
              <v-col cols="3" class="sub_tag_btn tag_square" @click="set_tag(card,'square')" v-ripple><v-icon :icon="isCardTaggedSquare ? 'mdi-square' : 'mdi-square-outline'" size="large" color="teal"/></v-col>
              <v-col cols="3" class="sub_tag_btn tag_triangle" @click="set_tag(card,'triangle')" v-ripple><v-icon :icon="isCardTaggedTriangle ? 'mdi-triangle' : 'mdi-triangle-outline'" size="large" color="pink"/></v-col>
              <v-col cols="3" class="sub_tag_btn tag_circle" @click="set_tag(card,'circle')" v-ripple><v-icon :icon="isCardTaggedCircle ? 'mdi-circle' : 'mdi-circle-outline'" size="large" color="indigo"/></v-col>
              <v-col cols="3" class="sub_tag_btn tag_cross" @click="set_tag(card,'cross')" v-ripple><v-icon :icon="isCardTaggedCross ? 'mdi-close-thick' : 'mdi-close-outline'" size="large" color="orange"/></v-col>
              <v-tooltip activator="parent" location="bottom">Tag cards for identification</v-tooltip>
            </v-row>
          </v-card>
          <v-card v-show="!isHovering" v-if="isCardOwned" class="tag_card_icons" color="transparent" :style={}>
            <v-row no-gutters align="center">
              <v-col cols="3" :class="{sub_tag_icon:true, tag_visible:isCardTaggedSquare, tag_invisible:!isCardTaggedSquare}"><v-icon icon="mdi-square" size="large" color="teal"/></v-col>
              <v-col cols="3" :class="{sub_tag_icon:true, tag_visible:isCardTaggedTriangle, tag_invisible:!isCardTaggedTriangle}"><v-icon icon="mdi-triangle" size="large" color="pink"/></v-col>
              <v-col cols="3" :class="{sub_tag_icon:true, tag_visible:isCardTaggedCircle, tag_invisible:!isCardTaggedCircle}"><v-icon icon="mdi-circle" size="large" color="indigo"/></v-col>
              <v-col cols="3" :class="{sub_tag_icon:true, tag_visible:isCardTaggedCross, tag_invisible:!isCardTaggedCross}"><v-icon icon="mdi-close-thick" size="large" color="orange"/></v-col>
              <v-tooltip activator="parent" location="bottom">Tag cards for identification</v-tooltip>
            </v-row>
          </v-card>
        </v-card>
    </v-hover>
</template>

<script>
export default {
    props: ['card','collection_stock','current_set_code', 'show_option', 'is_extra', 'base_set_total', 'extra_set_total', 'current_set_commons', 'current_set_uncommons', 'current_set_rares', 'current_set_mythics'],
    methods: {
        // passing the card images uri array and possible card faces object, return an image uri, prioritizing images uri
        getCardImage(uriArray,cardFacesArray){
          if(uriArray)
          {
              return uriArray['normal']
          }
          else if(cardFacesArray)
          {
              return cardFacesArray[0]['image_uris']['normal']
          }
          else return
        },
        add_card_to_stock(card_data){
          // first, we check if we already have any cards from this set; if not, we create a new empty set with this set's name
          if(!(card_data.set in this.collection_stock)) {
            var new_set = {
              cards:{},
              commons: 0,
              uncommons: 0,
              rares: 0,
              mythics: 0,
              total_commons: this.current_set_commons,
              total_uncommons: this.current_set_uncommons,
              total_rares: this.current_set_rares,
              total_mythics: this.current_set_mythics,
              printed_size: 0,  // for sets that have it, this tracks the base set size, which is SUPER helpful for my base/extra calcs
              base_set_owned: 0,
              extra_owned: 0,
              foils_owned: 0,
              base_set_total: this.base_set_total,
              extra_set_total: this.extra_set_total,
              full_set_every_single: 0,  // 'full set' parameters save the completion percentage for each definition of full set
              full_set_base_only: 0,
              full_set_one_each: 0,
              released_at: card_data.released_at
            }
            this.collection_stock[card_data.set] = new_set
          }
          
          // next, we check the existing card stock for copies; if yes, we add to the count; if not, we create a new card template for this card
          if(card_data.name in this.collection_stock[card_data.set].cards){
            if(card_data.collector_number in this.collection_stock[card_data.set].cards[card_data.name])
            {
              this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].count++
            }
            else
            {
              this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number] = {
                count: 1,
                foil: false
              }
              
              if(this.is_extra){
                this.collection_stock[card_data.set].extra_owned++
              } else {
                this.collection_stock[card_data.set].base_set_owned++
              }
            }
          } else {
            // create a new card object for that collector number
            const new_card = {
              [card_data.collector_number] : {
                count: 1,
                foil: false
              }
            }
            // append it to a new subset of cards in the set, rooted as the name of the card
            this.collection_stock[card_data.set].cards[card_data.name] = new_card
            // add to the appropriate total rarity count
            switch(card_data.rarity){
              case 'common':
                this.collection_stock[card_data.set].commons++
                break
              case 'uncommon':
              this.collection_stock[card_data.set].uncommons++
                break
              case 'rare':
              this.collection_stock[card_data.set].rares++
                break
              case 'mythic':
              this.collection_stock[card_data.set].mythics++
                break
              default:
                break
            }
            // set whether it's an extra card or base set card, for the total count
            if(this.is_extra){
              this.collection_stock[card_data.set].extra_owned++
            } else {
              this.collection_stock[card_data.set].base_set_owned++
            }
          }
          // recalculate the full set percentage counters for this set
          this.collection_stock[card_data.set].full_set_every_single = ((this.collection_stock[card_data.set].base_set_owned + this.collection_stock[card_data.set].extra_owned) / (this.collection_stock[card_data.set].base_set_total + this.collection_stock[card_data.set].extra_set_total))*100
          this.collection_stock[card_data.set].full_set_base_only = (this.collection_stock[card_data.set].base_set_owned / this.collection_stock[card_data.set].base_set_total)*100
          this.collection_stock[card_data.set].full_set_one_each = ((this.collection_stock[card_data.set].commons + this.collection_stock[card_data.set].uncommons + this.collection_stock[card_data.set].rares + this.collection_stock[card_data.set].mythics) / (this.current_set_commons + this.current_set_uncommons + this.current_set_rares + this.current_set_mythics))*100
          console.log("current collection stock",this.collection_stock)
        },
        remove_card_from_stock(card_data){
          // first, we check the existing card stock for copies; if more than 1, we just reduce the count by 1, else we remove the print entirely, and possibly the entire card name
          const total_of_this_print = this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].count
          if(total_of_this_print <= 1){
            // remove it from the foil tracker
            if(this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].foil)
            { 
              this.collection_stock[card_data.set].foils_owned-- 
            }
            delete this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number]
            // remove it from the base set/extra tracker
            if(this.is_extra){
              this.collection_stock[card_data.set].extra_owned--
            } else {
              this.collection_stock[card_data.set].base_set_owned--
            }
            // if there are no more prints of this card on this set, we remove it from the tracked rarity list
            if (JSON.stringify(this.collection_stock[card_data.set].cards[card_data.name]) === "{}")  // stringify an empty object returns "{}"... ugly but works
            {
              switch(card_data.rarity){
                case 'common':
                  this.collection_stock[card_data.set].commons--
                  break
                case 'uncommon':
                this.collection_stock[card_data.set].uncommons--
                  break
                case 'rare':
                this.collection_stock[card_data.set].rares--
                  break
                case 'mythic':
                this.collection_stock[card_data.set].mythics--
                  break
                default:
                  break
              }
              delete this.collection_stock[card_data.set].cards[card_data.name]
            }
          } else {
            this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].count--
          }
          // recalculate the full set percentage counters for this set
          this.collection_stock[card_data.set].full_set_every_single = ((this.collection_stock[card_data.set].base_set_owned + this.collection_stock[card_data.set].extra_owned) / (this.collection_stock[card_data.set].base_set_total + this.collection_stock[card_data.set].extra_set_total))*100
          this.collection_stock[card_data.set].full_set_base_only = (this.collection_stock[card_data.set].base_set_owned / this.collection_stock[card_data.set].base_set_total)*100
          this.collection_stock[card_data.set].full_set_one_each = ((this.collection_stock[card_data.set].commons + this.collection_stock[card_data.set].uncommons + this.collection_stock[card_data.set].rares + this.collection_stock[card_data.set].mythics) / (this.current_set_commons + this.current_set_uncommons + this.current_set_rares + this.current_set_mythics))*100
          console.log("current collection stock",this.collection_stock)
        },
        mark_card_as_foil(card_data){
          this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].foil = true
          this.collection_stock[card_data.set].foils_owned++
        },
        mark_card_as_nonfoil(card_data){
          this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number].foil = false
          this.collection_stock[card_data.set].foils_owned--
        },
        set_tag(card_data,tag){
          this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number]['tag_'+tag] = !this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number]['tag_'+tag]
          console.log("current tag for tag_"+tag,this.collection_stock[card_data.set].cards[card_data.name][card_data.collector_number]['tag_'+tag])
        },
    },
    computed: {
      isCardOwned: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
      },
      isCardFoil: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].foil == true
      },
      isCardTaggedSquare: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_square == true
      },
      isCardTaggedCircle: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_circle == true
      },
      isCardTaggedTriangle: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_triangle == true
      },
      isCardTaggedCross: function() {
        return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards 
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_cross == true
      },
      isCardVisible: function() {
        // show option 1 is 'all cards', 2 is 'only owned', and 3 is 'only unowned', so an owned card will show up as long as the option is not 3
        return (this.isCardOwned && this.show_option != 3) || (!this.isCardOwned && this.show_option != 2)
      }
    }
}
</script>

<style>
.v-btn {
  min-width: 0 !important;
}
.card_element {
  display: inline-block;
  position: relative;
}
.card_image {
  width: 100%; 
  opacity: 0.5;
  /* -webkit-filter: grayscale(1);
  filter: grayscale(1); */
}
.lit_up_card_image {
  opacity: 0.75;
  /* -webkit-filter: grayscale(0);
  filter: grayscale(0); */
}
.card_owned {
  opacity: 1;
  /* -webkit-filter: grayscale(0);
  filter: grayscale(0); */
}
.main_add_card_button {
  display:inline-block;
  position:absolute !important; 
  top: 10px;
  right: 10px;
  background-color: #E0F2F1;
}
.owned_card_controls {
  display:inline-block;
  position:absolute !important; 
  top: 10px;
  right: 10px;
  border-radius: 10px;
  width: 80px;
  height: 30px;
  padding: 0;
}
.btn_foil_modify {
  display:inline-block;
  position:absolute !important; 
  top: 10px;
  right: 100px;
  width: 30px;
}
.sub_remove_card_btn {
  background-color: #FF5252;
  height: 30px;
}
.sub_remove_card_btn:hover {
  background-color: #FF1744;
  cursor: pointer;
}
.sub_card_count {
  background-color: #E0F2F1;
  height: 30px;
}
.sub_add_card_btn {
  background-color: #1DE9B6;
  height: 30px;
}
.sub_add_card_btn:hover {
  background-color: #00BFA5;
  cursor: pointer;
}
.tag_card_controls {
  display:inline-block;
  position:absolute !important; 
  bottom: 15px;
  left: 10px;
  border-radius: 10px;
  width: 120px;
  height: 30px;
  padding: 0;
}
.sub_tag_btn {
  height: 30px;
}
.sub_tag_btn:hover {
  cursor: pointer;
}
.tag_square {
  background-color: #E0F2F1;
}
.tag_square:hover {
  background-color: #B2DFDB;
}
.tag_circle {
  background-color: #E8EAF6;
}
.tag_circle:hover {
  background-color: #C5CAE9;
}
.tag_triangle {
  background-color: #FCE4EC;
}
.tag_triangle:hover {
  background-color: #F8BBD0;
}
.tag_cross {
  background-color: #FFF3E0;
}
.tag_cross:hover {
  background-color: #FFE0B2;
}
.tag_card_icons {
  display:inline-block;
  position:absolute !important; 
  bottom: 15px;
  left: 10px;
  border-radius: 10px;
  width: 120px;
  height: 30px;
  padding: 0;
}
.sub_tag_icon {
  height: 30px;
}
.tag_visible {
  opacity: 0.5;
}
.tag_invisible {
  opacity: 0;
}
.foil_card_frame {
  background: linear-gradient(to bottom right, #b827fc 0%, #2c90fc 25%, #b8fd33 50%, #fec837 75%, #fd1892 100%) !important;
  box-sizing: border-box;
  height: 97.5%;
  width: 100%;
  overflow: hidden;
  position: absolute !important;
  display: block;
  top: 0;
  left: 0;
  opacity: 0.2;
}
</style>