<!-- This component represents a single card being rendered on the screen and all the associated buttons and thingamajigs -->
<template>
  <v-hover v-slot="{ isHovering, props }" v-if="isCardVisible">
    <v-card :class="{ 'on-hover': isHovering, 'card-element': true }" :="props" flat>
      <img :src="getCardImage(card['image_uris'], card['card_faces'])" class="card_image"
        :class="{ 'lit_up_card_image': isHovering, 'card_owned': isCardOwned }">
      <v-card name="foil_overlay" :class="{ 'foil_card_frame': isCardFoil }"></v-card>
      <v-btn @click="add_card_to_stock(card)" class="main_add_card_button" v-show="isHovering" v-if="!isCardOwned"
        density="comfortable">
        <v-icon icon="mdi-plus-thick" size="x-large" color="teal-accent-3" />
      </v-btn>
      <v-btn @click="mark_card_as_foil(card)" class="btn_foil_modify" v-show="isHovering && !isCardOnlyNonfoil"
        v-if="isCardOwned && !isCardFoil" :disabled="isCardOnlyFoil" color="purple-lighten-3" density="comfortable">
        <v-icon icon="mdi-star-outline" size="x-large" color="white" />
        <v-tooltip activator="parent" location="bottom">Set as Foil</v-tooltip>
      </v-btn>
      <v-btn @click="mark_card_as_nonfoil(card)" class="btn_foil_modify" v-show="isHovering"
        v-if="isCardOwned && isCardFoil" :disabled="isCardOnlyFoil" color="purple-lighten-3" density="comfortable">
        <v-icon icon="mdi-star" size="x-large" color="white" />
        <v-tooltip activator="parent" location="bottom">Remove Foil</v-tooltip>
      </v-btn>
      <v-card v-show="isHovering" v-if="isCardOwned" class="owned_card_controls">
        <v-row no-gutters align="center">
          <v-col cols="4" class="sub_remove_card_btn" @click="remove_card_from_stock(card)"><v-icon
              icon="mdi-minus-thick" size="large" color="red-lighten-5" /></v-col>
          <v-col cols="4" class="sub_card_count">
            <p class="card_count" :class="{ dark_mode_card_count: dark_mode }">{{
              this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].count }}
            </p>
          </v-col>
          <v-col cols="4" class="sub_add_card_btn" @click="add_card_to_stock(card)"><v-icon icon="mdi-plus-thick"
              size="large" color="teal-lighten-5" /></v-col>
        </v-row>
      </v-card>
      <!-- chip below shows the default price of the card: nonfoil if it exists, else foil/etched if that's the only version -->
      <v-chip v-show="isHovering && show_price"
        v-if="card.prices['usd'] || card.prices['usd_foil'] || card.prices['usd_etched']" variant="flat"
        class="card_price_element" :color="isCardOwned && (!isCardFoil || isCardOnlyFoil) ? '#FFF9C4' : 'white'"
        size="x-small">
        <p style="color:#7E57C2; font-size:15px;">{{ !card.prices['usd'] ? '✪' : '' }}</p> ${{ card.prices['usd'] ?
          card.prices['usd'] : (card.prices['usd_foil'] ? card.prices['usd_foil'] : card.prices['usd_etched']) }}
      </v-chip>
      <!-- chip below only shows if the nonfoil price exists AND a foil/etched also exists -->
      <v-chip v-show="isHovering && show_price"
        v-if="card.prices['usd'] && (card.prices['usd_foil'] || card.prices['usd_etched'])" variant="flat"
        class="card_price_element_foil" :color="isCardOwned && isCardFoil && !isCardOnlyFoil ? '#FFF9C4' : 'white'"
        size="x-small">
        <p style="color:#7E57C2; font-size:15px;">✪</p> ${{ card.prices['usd_foil'] ? card.prices['usd_foil'] :
          card.prices['usd_etched'] }}
      </v-chip>
      <v-card v-show="isHovering" v-if="isCardOwned" class="tag_card_controls">
        <v-row no-gutters align="center">
          <v-col cols="3" class="sub_tag_btn tag_square" @click="set_tag(card, 'square')" v-ripple><v-icon
              :icon="isCardTaggedSquare ? 'mdi-square' : 'mdi-square-outline'" size="large" color="teal" /></v-col>
          <v-col cols="3" class="sub_tag_btn tag_triangle" @click="set_tag(card, 'triangle')" v-ripple><v-icon
              :icon="isCardTaggedTriangle ? 'mdi-triangle' : 'mdi-triangle-outline'" size="large"
              color="pink" /></v-col>
          <v-col cols="3" class="sub_tag_btn tag_circle" @click="set_tag(card, 'circle')" v-ripple><v-icon
              :icon="isCardTaggedCircle ? 'mdi-circle' : 'mdi-circle-outline'" size="large" color="indigo" /></v-col>
          <v-col cols="3" class="sub_tag_btn tag_cross" @click="set_tag(card, 'cross')" v-ripple><v-icon
              :icon="isCardTaggedCross ? 'mdi-close-thick' : 'mdi-close-outline'" size="large" color="orange" /></v-col>
          <v-tooltip activator="parent" location="bottom">Tag cards for identification</v-tooltip>
        </v-row>
      </v-card>
      <v-card v-show="!isHovering" v-if="isCardOwned" class="tag_card_icons" variant="flat" color="transparent"
        :style={}>
        <v-row no-gutters align="center">
          <v-col cols="3"
            :class="{ sub_tag_icon: true, tag_visible: isCardTaggedSquare, tag_invisible: !isCardTaggedSquare }"><v-icon
              icon="mdi-square" size="large" color="teal" /></v-col>
          <v-col cols="3"
            :class="{ sub_tag_icon: true, tag_visible: isCardTaggedTriangle, tag_invisible: !isCardTaggedTriangle }"><v-icon
              icon="mdi-triangle" size="large" color="pink" /></v-col>
          <v-col cols="3"
            :class="{ sub_tag_icon: true, tag_visible: isCardTaggedCircle, tag_invisible: !isCardTaggedCircle }"><v-icon
              icon="mdi-circle" size="large" color="indigo" /></v-col>
          <v-col cols="3"
            :class="{ sub_tag_icon: true, tag_visible: isCardTaggedCross, tag_invisible: !isCardTaggedCross }"><v-icon
              icon="mdi-close-thick" size="large" color="orange" /></v-col>
          <v-tooltip activator="parent" location="bottom">Tag cards for identification</v-tooltip>
        </v-row>
      </v-card>
    </v-card>
  </v-hover>
</template>

<script>
import { authFetch } from './authFetch.js'

export default {
  props: ['card', 'user_id', 'csrf_token', 'collection_stock', 'current_set_code', 'show_price', 'dark_mode', 'is_extra', 'base_set_total', 'extra_set_total', 'current_set_commons', 'current_set_uncommons', 'current_set_rares', 'current_set_mythics'],
  methods: {
    // passing the card images uri array and possible card faces object, return an image uri, prioritizing images uri
    getCardImage(uriArray, cardFacesArray) {
      if (uriArray) {
        return uriArray['normal']
      }
      else if (cardFacesArray) {
        return cardFacesArray[0]['image_uris']['normal']
      }
      else return
    },
    // triggers when the user clicks the "+" button to add a card to stock
    async add_card_to_stock(card_data) {
      console.log("Card data clicked: ",card_data)
      
      await this.create_new_set_if_necessary()

      if (!(card_data.set_code in this.collection_stock)) {
        var new_set = {
          cards: {},
          commons: 0,
          uncommons: 0,
          rares: 0,
          mythics: 0,
          total_commons: this.current_set_commons,
          total_uncommons: this.current_set_uncommons,
          total_rares: this.current_set_rares,
          total_mythics: this.current_set_mythics,
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
        this.collection_stock[card_data.set_code] = new_set
      }

      // this data block will eventually be passed to the backend to update the relevant stat points
      var updated_set = {
        card_owner_id: this.user_id,
        set_code: this.current_set_code
      }

      // next, we check the existing card stock for copies; if yes, we add to the count; if not, we create a new card template for this card
      if (card_data.name in this.collection_stock[card_data.set_code].cards) {
        if (card_data.collector_number in this.collection_stock[card_data.set_code].cards[card_data.name]) {
          this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].count++
          const count = this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].count
          this.update_card(this.user_id, card_data.set_code, card_data.collector_number, count) 
        }
        else {
          // persist new card in database, with standard values
          await this.create_new_card(this.user_id, card_data.name, this.current_set_code, card_data.collector_number)
          // create a new card object; if the card is only available in foil, foil is already true
          this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number] = {
            count: 1,
            foil: (this.card.foil || this.card.finishes.includes("etched")) && !this.card.nonfoil,
            extra: this.is_extra,
            image: this.getCardImage(this.card['image_uris'], this.card['card_faces'])?.replace("https://cards.scryfall.io/normal/front/", "")
          }
          // add to the foil tally if it's a foil only card
          if ((this.card.foil || this.card.finishes.includes("etched")) && !this.card.nonfoil){
            this.collection_stock[card_data.set_code].foils_owned++
            updated_set.foils_owned = this.collection_stock[card_data.set_code].foils_owned
          }

          if (this.is_extra) {
            this.collection_stock[card_data.set_code].extra_owned++
            updated_set.extra_set_owned = this.collection_stock[card_data.set_code].extra_owned
          } else {
            this.collection_stock[card_data.set_code].base_set_owned++
            updated_set.base_set_owned = this.collection_stock[card_data.set_code].base_set_owned
          }
        }
      } else {
        // persist new card in database, with standard values
        await this.create_new_card(this.user_id, card_data.name, this.current_set_code, card_data.collector_number)
        // create a new card object; if the card is only available in foil, foil is already true
        const new_card = {
          [card_data.collector_number]: {
            count: 1,
            foil: (this.card.foil || this.card.finishes.includes("etched")) && !this.card.nonfoil,
            extra: this.is_extra,
            image: this.getCardImage(this.card['image_uris'], this.card['card_faces'])?.replace("https://cards.scryfall.io/normal/front/", "")
          }
        }
        // append it to a new subset of cards in the set, rooted as the name of the card
        this.collection_stock[card_data.set_code].cards[card_data.name] = new_card
        // add to the foil tally if it's a foil only card
        if ((this.card.foil || this.card.finishes.includes("etched")) && !this.card.nonfoil) {
          this.collection_stock[card_data.set_code].foils_owned++
          updated_set.foils_owned = this.collection_stock[card_data.set_code].foils_owned
        }
        // add to the appropriate total rarity count
        switch (card_data.rarity) {
          case 'common':
            this.collection_stock[card_data.set_code].commons++
            updated_set.commons_count = this.collection_stock[card_data.set_code].commons
            break
          case 'uncommon':
            this.collection_stock[card_data.set_code].uncommons++
            updated_set.uncommons_count = this.collection_stock[card_data.set_code].uncommons
            break
          case 'rare':
            this.collection_stock[card_data.set_code].rares++
            updated_set.rares_count = this.collection_stock[card_data.set_code].rares
            break
          case 'mythic':
            this.collection_stock[card_data.set_code].mythics++
            updated_set.mythics_count = this.collection_stock[card_data.set_code].mythics
            break
          default:
            break
        }
        // set whether it's an extra card or base set card, for the total count
        if (this.is_extra) {
          this.collection_stock[card_data.set_code].extra_owned++
          updated_set.extra_set_owned = this.collection_stock[card_data.set_code].extra_owned
        } else {
          this.collection_stock[card_data.set_code].base_set_owned++
          updated_set.base_set_owned = this.collection_stock[card_data.set_code].base_set_owned
        }
      }
      // recalculate the full set percentage counters for this set
      const completion_data = this.calculate_completion_for_set(card_data)
      updated_set.full_set_base_only = completion_data.full_set_base_only
      updated_set.full_set_every_single = completion_data.full_set_every_single
      updated_set.full_set_one_each = completion_data.full_set_one_each
      // update the set data on the db with the passed values
      this.update_set(updated_set)
      console.log("current collection stock", this.collection_stock)
    },
    // --------------------------------------------------------------------------------------------------------------- //
    // --------------------------------------------------------------------------------------------------------------- //
    remove_card_from_stock(card_data) {
      // this data block will eventually be passed to the backend to update the relevant stat points
      var updated_set = {
        card_owner_id: this.user_id,
        set_code: this.current_set_code
      }

      // first, we check the existing card stock for copies; if more than 1, we just reduce the count by 1, else we remove the print entirely, and possibly the entire card name
      const total_of_this_print = this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].count
      if (total_of_this_print <= 1) {
        // remove it from the foil tracker
        if (this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].foil) {
          this.collection_stock[card_data.set_code].foils_owned--
          updated_set.foils_owned = this.collection_stock[card_data.set_code].foils_owned
        }
        delete this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number]
        // remove it from the base set/extra tracker
        if (this.is_extra) {
          this.collection_stock[card_data.set_code].extra_owned--
          updated_set.extra_set_owned = this.collection_stock[card_data.set_code].extra_owned
        } else {
          this.collection_stock[card_data.set_code].base_set_owned--
          updated_set.base_set_owned = this.collection_stock[card_data.set_code].base_set_owned
        }
        // if there are no more prints of this card on this set, we remove it from the tracked rarity list
        if (JSON.stringify(this.collection_stock[card_data.set_code].cards[card_data.name]) === "{}")  // stringify an empty object returns "{}"... ugly but works
        {
          switch (card_data.rarity) {
            case 'common':
              this.collection_stock[card_data.set_code].commons--
              updated_set.commons_count = this.collection_stock[card_data.set_code].commons
              break
            case 'uncommon':
              this.collection_stock[card_data.set_code].uncommons--
              updated_set.uncommons_count = this.collection_stock[card_data.set_code].uncommons
              break
            case 'rare':
              this.collection_stock[card_data.set_code].rares--
              updated_set.rares_count = this.collection_stock[card_data.set_code].rares
              break
            case 'mythic':
              this.collection_stock[card_data.set_code].mythics--
              updated_set.mythics_count = this.collection_stock[card_data.set_code].mythics
              break
            default:
              break
          }
          delete this.collection_stock[card_data.set_code].cards[card_data.name]
        }
        // remove the card from the database
        this.delete_card(this.user_id, card_data.set_code, card_data.collector_number)
        // recalculate the full set percentage counters for this set
        const completion_data = this.calculate_completion_for_set(card_data)
        updated_set.full_set_base_only = completion_data.full_set_base_only
        updated_set.full_set_every_single = completion_data.full_set_every_single
        updated_set.full_set_one_each = completion_data.full_set_one_each
        // update the set data on the db with the passed values
        this.update_set(updated_set)
      } else {  
        // we have more than 1 on the count, so we just lower the number
        this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].count--
        const count = this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].count
        // update the card on the database by removing one from the count
        this.update_card(this.user_id, card_data.set_code, card_data.collector_number, count) 
      }
    },
    // --------------------------------------------------------------------------------------------------------------- //
    // --------------------------------------------------------------------------------------------------------------- //
    mark_card_as_foil(card_data) {
      this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].foil = true
      this.collection_stock[card_data.set_code].foils_owned++
      const foils_owned = this.collection_stock[card_data.set_code].foils_owned
      const updated_set = {
        card_owner_id: this.user_id,
        set_code: this.current_set_code,
        foils_owned: foils_owned
      }
      this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, true)
      this.update_set(updated_set)
    },
    mark_card_as_nonfoil(card_data) {
      this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number].foil = false
      this.collection_stock[card_data.set_code].foils_owned--
      const foils_owned = this.collection_stock[card_data.set_code].foils_owned
      const updated_set = {
        card_owner_id: this.user_id,
        set_code: this.current_set_code,
        foils_owned: foils_owned
      }
      this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, false)
      this.update_set(updated_set)
    },
    // uses current data to calculate how much of the set the user has obtained, for each kind of metric
    calculate_completion_for_set(card_data) {
      const full_set_every_single = ((this.collection_stock[card_data.set_code].base_set_owned + this.collection_stock[card_data.set_code].extra_owned) / (this.collection_stock[card_data.set_code].base_set_total + this.collection_stock[card_data.set_code].extra_set_total)) * 100
      const full_set_base_only = (this.collection_stock[card_data.set_code].base_set_owned / this.collection_stock[card_data.set_code].base_set_total) * 100
      const full_set_one_each = ((this.collection_stock[card_data.set_code].commons + this.collection_stock[card_data.set_code].uncommons + this.collection_stock[card_data.set_code].rares + this.collection_stock[card_data.set_code].mythics) / (this.current_set_commons + this.current_set_uncommons + this.current_set_rares + this.current_set_mythics)) * 100
      this.collection_stock[card_data.set_code].full_set_every_single = full_set_every_single
      this.collection_stock[card_data.set_code].full_set_base_only = full_set_base_only
      this.collection_stock[card_data.set_code].full_set_one_each = full_set_one_each
      return {  // return the calculated values so they can be pushed to the set info on the database as well
        full_set_every_single : full_set_every_single,
        full_set_base_only : full_set_base_only,
        full_set_one_each : full_set_one_each
      }
    },
    set_tag(card_data, tag) {
      const tagVal = !this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number]['tag_' + tag]
      switch(tag){
        case 'square':
          this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, null, tagVal)
          break;
        case 'circle':
          this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, null, null, tagVal)
          break;
        case 'triangle':
          this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, null, null, null, tagVal)
          break;
        case 'cross':
          this.update_card(this.user_id, card_data.set_code, card_data.collector_number,null, null, null, null, null, tagVal)
          break;
        default:
          console.log("Code hit unexpected default behavior on set_tag")
          break;
      }
      this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number]['tag_' + tag] = !this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number]['tag_' + tag]
      console.log("current tag for tag_" + tag, this.collection_stock[card_data.set_code].cards[card_data.name][card_data.collector_number]['tag_' + tag])
    },
    // --------------------------------------------------------------------------------------------------------------- //
    // --------------------------------------------------------------------------------------------------------------- //
    async create_new_card(user_id, card_name, set_code, collector_number) {
      // create new card object with all of the necessary data
      const new_card = {
        card_owner_id: user_id,
        set_code: set_code,
        card_name: card_name,
        collector_number: collector_number,
        card_count: 1,
        is_foil: this.isCardOnlyFoil,
        is_considered_extra: this.is_extra,
        is_tagged_square: false,
        is_tagged_circle: false,
        is_tagged_triangle: false,
        is_tagged_cross: false,
      }
      console.log("Persisting the card: ",new_card)
      // post the new card to the server
      const postNewCard = await authFetch('/mtg-collectron/owncard/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.csrf_token
        },
        body: JSON.stringify(new_card)
      })
      if (postNewCard.ok) console.log("Posted new card "+ card_name +" successfully"); else console.log("Posting new card "+ card_name +" failed with error "+postNewCard.status);
      return postNewCard.ok // comes back true or false depending if call succeeds
    },
    // update_card is called whenever one or more fields are changed in a card that already exists
    async update_card(user_id, set_code, collector_number, card_count, is_foil, is_tagged_square, is_tagged_circle, is_tagged_triangle, is_tagged_cross) {
      // create card object with basic identifying data
      const updated_card = {
        card_owner_id: user_id,
        set_code: set_code,
        collector_number: collector_number
      }
      if(card_count != null) {updated_card.card_count = card_count}
      if(is_foil != null) {updated_card.is_foil = is_foil}
      if(is_tagged_square != null) {updated_card.is_tagged_square = is_tagged_square}
      if(is_tagged_circle != null) {updated_card.is_tagged_circle = is_tagged_circle}
      if(is_tagged_triangle != null) {updated_card.is_tagged_triangle = is_tagged_triangle}
      if(is_tagged_cross != null) {updated_card.is_tagged_cross = is_tagged_cross}

      console.log("Updating the card: ",updated_card) 
      // post the new card to the server
      const updateCardCall = await authFetch('/mtg-collectron/owncard/', {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.csrf_token
        },
        body: JSON.stringify(updated_card)
      })
      if (updateCardCall.ok) console.log("Updated card "+ collector_number +" successfully"); else console.log("Updating card "+ collector_number +" failed with error "+updateCardCall.status);
      return updateCardCall.ok // comes back true or false depending if call succeeds
    },
    // delete_card removes an existing card from the user's collection
    async delete_card(user_id, set_code, collector_number) {
      const card_to_delete = {
        card_owner_id: user_id,
        set_code: set_code,
        collector_number: collector_number
      }

      console.log("Deleting the card: ", card_to_delete)
      const deleteCardCall = await authFetch('/mtg-collectron/owncard/', {
        method: 'DELETE',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.csrf_token
        },
        body: JSON.stringify(card_to_delete)
      })
      if (deleteCardCall.ok) console.log("Deleted card "+ collector_number +" successfully"); else console.log("Deleting card "+ collector_number +" failed with error "+deleteCardCall.status);
      return deleteCardCall.ok
    },
    // checks if set data exists for user in database; creates it if needed
    async create_new_set_if_necessary(){
      // first, we check if we already have any cards from this set; if not, we create a new empty set with this set's name
      const setCheck = await authFetch('/mtg-collectron/user-set-info/' + this.user_id + "/" + this.current_set_code, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })

      // server returns "NOT_FOUND" (404) if there's no data found
      if (setCheck.status == 404) {
        // TODO: maybe we can get rid of saving user set data entirely?
        var new_set = {
          card_owner_id: this.user_id,
          set_code: this.current_set_code,
          commons_count: 0,
          uncommons_count: 0,
          rares_count: 0,
          mythics_count: 0,
          base_set_owned: 0,
          extra_set_owned: 0,
          foils_owned: 0,
          full_set_every_single: 0,  // 'full set' parameters save the completion percentage for each definition of full set
          full_set_base_only: 0,
          full_set_one_each: 0
        }

        // post the new set to the server with empty parameters
        const postNewSet = await authFetch('/mtg-collectron/user-set-info/', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': this.csrf_token
          },
          body: JSON.stringify(new_set)
        })
        if(postNewSet.ok){ console.log("Successfully created set entry for "+this.current_set_code+" in the database.") }
        else { console.log("Failed to create set info for set "+this.current_set_code+" on the database.") }
      }
    },
    // update_set is called whenever one or more fields are changed in a set that already exists
    async update_set(updated_set) {
      console.log("Updating the set: ", updated_set)
      const updateSetCall = await authFetch('/mtg-collectron/user-set-info/', {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': this.csrf_token
        },
        body: JSON.stringify(updated_set)
      })
      if (updateSetCall.ok) console.log("Updated set "+ updated_set.set_code +" successfully"); else console.log("Updating set "+ updated_set.set_code +" failed with error "+updateSetCall.status);
      return updateSetCall.ok
    }
  },
  // --------------------------------------------------------------------------------------------------------------- //
  // --------------------------------------------------------------------------------------------------------------- //
  computed: {
    isCardOwned: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
    },
    isCardFoil: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].foil == true
    },
    isCardTaggedSquare: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_square == true
    },
    isCardTaggedCircle: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_circle == true
    },
    isCardTaggedTriangle: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_triangle == true
    },
    isCardTaggedCross: function () {
      return this.collection_stock[this.current_set_code] && this.card.name in this.collection_stock[this.current_set_code].cards
        && this.card.collector_number in this.collection_stock[this.current_set_code].cards[this.card.name]
        && this.collection_stock[this.current_set_code].cards[this.card.name][this.card.collector_number].tag_cross == true
    },
    isCardVisible: function () {
      // show option 1 is 'all cards', 2 is 'only owned', and 3 is 'only unowned', so an owned card will show up as long as the option is not 3
      return true
      // return (this.isCardOwned && this.show_option != 3) || (!this.isCardOwned && this.show_option != 2)
    },
    isCardOnlyNonfoil: function () {
      // identifies whether this card is only available in nonfoil
      return this.card.nonfoil && !this.card.foil && !this.card.finishes.includes("etched")
    },
    isCardOnlyFoil: function () {
      // identifies whether this card is only available in nonfoil
      return (this.card.foil || this.card.finishes.includes("etched")) && !this.card.nonfoil
    },
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
  display: inline-block;
  position: absolute !important;
  top: 10px;
  right: 10px;
  background-color: #E0F2F1;
}

.owned_card_controls {
  display: inline-block;
  position: absolute !important;
  top: 10px;
  right: 10px;
  border-radius: 10px;
  width: 80px;
  height: 30px;
  padding: 0;
}

.card_price_element {
  display: inline-block;
  position: absolute !important;
  top: 45px;
  right: 10px;
  height: 20px;
  padding: 0;
  font-family: 'Aoboshi One', "Lucida Console", "Courier New", monospace;
  cursor: default;
}

.card_price_element_foil {
  display: inline-block;
  position: absolute !important;
  top: 68px;
  right: 10px;
  height: 20px;
  padding: 0;
  font-family: 'Aoboshi One', "Lucida Console", "Courier New", monospace;
  cursor: default;
}

.btn_foil_modify {
  display: inline-block;
  position: absolute !important;
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

.dark_mode_card_count {
  color: black;
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
  display: inline-block;
  position: absolute !important;
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
  display: inline-block;
  position: absolute !important;
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