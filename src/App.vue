<template>
  <v-app>
    <v-overlay :model-value="loading" class="align-center justify-center">
      <v-progress-circular color="primary" indeterminate size="64"/>
    </v-overlay>
    <v-overlay persistent :model-value="card_finder_window_active" class="align-center justify-center">
      <v-card class="card_finder_window">
        <v-card-item>
          <v-row class="import_window_header align-center">
            <v-col cols="6"><h2>Card Finder</h2></v-col>
            <v-spacer/>
            <v-col cols="1">
              <v-tooltip text="/n" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary"/>
                </template>
                <p>Searches your card collection for matches with the typed card name</p>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-item>
        <v-divider/>
        <v-text-field v-model="card_finder_text" label="Search" autofocus prepend-inner-icon="mdi-magnify" class="card_finder_text_field" variant="outlined"/>
        <!-- <v-card class="align-right">
          <input type="checkbox" value="tag_square_marked" v-model="tags_selected" class="tag_check">
          <label for="tag_square_marked" style="display: inline-block;">■</label>
        </v-card> -->
        <v-list nav class="card_finder_results_list align-left" v-show="card_finder_results.length > 0">
          <v-list-item v-for="card in card_finder_results" :title="card.formattedCardName" @click="goToFoundCard(card.cardName,card.cardSet)"  :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" />
        </v-list>
        <v-card-actions>
          <v-spacer/>
          <v-col cols="3"><v-btn @click="card_finder_window_active=false; card_finder_text = ''" variant="outlined">Close</v-btn></v-col>
        </v-card-actions>
      </v-card>
    </v-overlay>
    <v-overlay persistent :model-value="decklist_finder_window_active" class="align-center justify-center">
      <v-card class="import_window">
        <v-card-item>
          <v-row class="import_window_header align-center">
            <v-col cols="6"><h2>Decklist Finder</h2></v-col>
            <v-spacer/>
            <v-col cols="1">
              <v-tooltip text="/n" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary"/>
                </template>
                <p>Searches your collection for a list of cards, one per line, and returns the ones it matches.</p>
                <p class="mb-0">You can use either the Moxfield syntax (e.g. "1 Loran's Escape (BRO) *F*") to look for specific prints only,</p>
                <p class="mb-0">or MTGO syntax (e.g. "1 Mox Diamond") to get any printing of it.</p>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-card-item>
        <v-divider/>
        <v-radio-group inline v-model="decklist_finder_priority" density="compact" hide-details style="display:inline-block;">
          <v-radio color="primary" label="Prioritize Oldest Printing" value="oldest"/>
          <v-radio color="primary" label="Prioritize Newest Printing" value="newest"/>
        </v-radio-group>
        <v-textarea v-model="decklist_finder_text" autofocus class="import_text_field" variant="outlined"/>
        <v-row>
          <v-spacer/>
          <v-col cols="3"><v-btn @click="perform_decklist_finder_search">Find List</v-btn></v-col>
          <v-col cols="3"><v-btn @click="decklist_finder_window_active=false; decklist_finder_text = ''">Close</v-btn></v-col>
        </v-row>
      </v-card>
    </v-overlay>
    <v-overlay persistent :model-value="decklist_finder_results_window_active" class="align-center justify-center">
      <v-card class="decklist_finder_results_window">
        <v-card-item> <h2 style="text-align: center;">Search Results</h2> </v-card-item>
        <v-divider/>
        <v-list nav class="card_finder_results_list align-left" v-show="decklist_finder_results_processed.length > 0">
          <!-- <v-list-item v-for="card in decklist_finder_results_processed" style="display: inline-block; width: auto;" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'"> -->
          <v-card v-for="card in decklist_finder_results_processed" :class="{ 'decklist_finder_results_list_item' : true, 'tertiary_hover_dark' : page_options.dark_mode, 'tertiary_hover_light' : !page_options.dark_mode }" :flat="true">
            <!-- <v-icon icon="mdi-check-bold" size="large" color="primary" @click="mark_decklist_card_as_done(card)"/> -->
            <v-tooltip text="/n" location="bottom" :open-delay="700">
              <template v-slot:activator="{ props }">
                <v-icon :="props" icon="mdi-check-bold" @click="mark_decklist_card_as_done(card)" size="large" color="primary"/>
              </template>
              <p>Mark as done, removing from list</p>
            </v-tooltip>
            <!-- <v-icon icon="mdi-debug-step-over" size="large" color="primary" @click="skip_decklist_card(card)"/> -->
            <v-tooltip text="/n" location="bottom" :open-delay="700">
              <template v-slot:activator="{ props }">
                <v-icon :="props" icon="mdi-debug-step-over" @click="skip_decklist_card(card)" size="large" color="primary"/>
              </template>
              <p>Skip this printing, tries to use next printings if available</p>
            </v-tooltip>
            <p class="decklist_finder_results_text">{{ card.amount + "x " + card.formattedCardName }}</p>  
          </v-card>
        </v-list>
        <v-card-item v-show="decklist_finder_results_processed.length == 0"> <h3>There are no cards to display.</h3> </v-card-item>
        <v-card-actions>
          <v-spacer/>
          <v-col cols="3"><v-btn @click="decklist_finder_results_window_active=false; decklist_finder_results_processed.value = []" variant="outlined">Close</v-btn></v-col>
        </v-card-actions>
      </v-card>
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
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary"/>
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
          <v-radio color="primary" label="Moxfield" value="moxfield"/>
          <v-radio color="primary" label="Native" value="native"/>
        </v-radio-group>
        <v-textarea v-model="import_text" autofocus class="import_text_field" variant="outlined"/>
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
        <p v-show="import_errors == '' && import_syntax == 'native'">Imported and replaced collection succesfully.</p>
        <p v-show="import_errors && import_syntax == 'native'" style="padding:4px;">Failed to import the data. Make sure you copy and paste all of the characters. In case of importing an unrelated JSON object, I will not stop you from shooting your own foot, the site will very likely stop working properly until you clear all data again.</p>
        <br/>
        <p v-show="import_errors.length > 0">The following lines could not be imported:</p>
        <br v-show="import_errors.length > 0"/>
        <p v-show="import_errors">{{ import_errors }}</p>
      </v-card>
    </v-overlay>
    <v-overlay persistent :model-value="export_window_active" class="align-center justify-center">
      <v-card class="export_window">
        <v-card-item>
          <v-row class="import_window_header align-center">
            <v-col cols="6"><h2>Export Cards</h2></v-col>
            <v-spacer/>
            <v-col cols="1">
              <v-tooltip text="/n" location="bottom">
                <template v-slot:activator="{ props }">
                  <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary"/>
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
          <v-col cols="5"><v-btn @click="copyCollectionToClipboard">Copy to Clipboard</v-btn></v-col>
          <v-col cols="3"><v-btn @click="export_window_active=false">Close</v-btn></v-col>
        </v-row>
      </v-card>
    </v-overlay>
    <v-overlay id="about_window" :model-value="about_window_active" class="align-center justify-center" @click:outside="about_window_active = false">
      <v-card class="about_window">
        <v-card-item>
          <h2>About the Collectron</h2>
        </v-card-item>
        <v-divider/>
        <p style="padding:4px; font-size: 13px;">This website has been built from scratch and maintained by Guilherme Santana, with Vue/Vuetify, tested on Chrome desktop and Firefox mobile. I'm sure there are way better collection tools out there, but none that did quite what I wanted.</p>
        <p style="padding:4px; font-size: 13px;">The site is presented as-is - consider it an ongoing beta - and I make no guarantee about its accuracy, continued functionality, or backwards compatibility of new functions, but I hope you enjoy using it nonetheless.</p>
        <br/>
        <p style="padding:4px; font-size: 13px;">Magic: the Gathering, all card images, symbols and information associated with it, are copyrighted by Wizards of the Coast LLC, and I'm not affiliated with or endorsed by them.</p>
        <p style="padding:4px; font-size: 13px;">Card and set information, data searches, and visual information such as card and set icon pictures, are all sourced from Scryfall and its API. This site is not affiliated with them in any way, but I'm otherwise very grateful for their accessibility.</p>
        <br/>
        <v-card-actions>
          <v-spacer/>
          <v-btn @click="about_window_active=false" variant="outlined" style="margin-right: 10px; margin-bottom: 10px;">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-overlay>
    <v-snackbar v-model="toast" :timeout="2000">Copied to clipboard!</v-snackbar>
    <v-app-bar color="primary">
      <v-btn @click="drawer = !drawer">
        <v-icon icon="mdi-chevron-right-circle" size="x-large" v-if="!drawer"/>
        <v-icon icon="mdi-chevron-left-circle" size="x-large" v-if="drawer"/>
        <p style="margin-left: 10px;">Set Navigation</p>
      </v-btn>
      <v-spacer/>
      <v-btn @click="settings = !settings">
        <v-icon icon="mdi-menu" size="x-large"/>
      </v-btn>
    </v-app-bar>
    <v-main class="card_list_main" v-if="current_set && current_set_base_cards">
      <v-sheet class="card_list_body rounded-lg">
        <v-card id="set_page_title_card" :height="isMobile ? 140 : 100" flat>
          <div>
            <p class="set_page_title">{{ current_set.name }} ({{ current_set.code.toUpperCase() }})</p>
          </div>
          <div style="display:inline-block; margin-right: 30px;">
            <p class="set_page_subtitle">Release Date:</p><p class="set_page_subtext">{{ current_set['released_at'] }}</p>
          </div>
          <div style="display:inline-block">
            <p class="set_page_subtitle">Set Type:</p><p class="set_page_subtext">{{ current_set['set_type'] }}</p>
          </div>
        </v-card>
        <v-row>
          <v-col cols="12" sm="3">
            <v-text-field v-model="card_search" label="Card Search" prepend-inner-icon="mdi-magnify" variant="outlined" color="primary" density="compact" clearable @click:clear="card_search = ''"/>
          </v-col>
          <v-spacer v-show="!isMobile"/>
          <v-col cols="12" sm="3">
            <v-select v-model="page_options.card_per_page_option_selected" label="Cards per Page" :items="card_per_page_options" return-object density="compact" variant="outlined"/>
          </v-col>
        </v-row>
        <v-card class="page_header">
          <v-card class="set_stats_banner" flat>
            <v-row style="height: 70px;" align="center" >
              <v-col><p>Base Set:</p><p>{{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p></v-col>
              <v-divider vertical/>
              <v-col v-if="current_set_extra_cards_qty > 0">
                <p style="display:inline;">Extra Cards:</p>
                <v-tooltip text="/n" location="bottom" style="display:inline;">
                  <template v-slot:activator="{ props }">
                    <v-icon :="props" icon="mdi-help-circle" size="medium" color="primary" style="margin-left:10px;"/>
                  </template>
                  <p>Showcase frame cards, extended art carts, borderless cards, Buy-a-Box, etc</p>
                </v-tooltip>
                <p>{{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p></v-col>
              <v-divider vertical v-if="current_set_extra_cards_qty > 0"/>
              <v-col><p>Grand Total:</p><p>{{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p></v-col>
              <v-col><p>Foil Cards:</p><p>{{ current_set_owned_foils }}/{{ current_set_base_cards_qty+current_set_extra_cards_qty }}</p></v-col>
            </v-row>
          </v-card>
          <v-progress-linear height="15" v-model="getProgressForSet" :color="getProgressForSet < 100 ? 'primary' : 'amber-lighten-2' ">
            <template v-slot:default="{ value }">
              <strong>{{ Math.round(value * 10) / 10 }}%</strong>
            </template>
          </v-progress-linear>
        </v-card>
        <v-sheet name="normal_cards_holder">
          <v-row no-gutters>
            <v-col v-for="(item,index) in current_set_base_cards.filter((card) => (card.name.toLowerCase().includes(card_search.toLowerCase()) || card_search == '')).slice(pageSliceStart,pageSliceEnd)" cols="6" sm="6" md="4" lg="3" >
              <CardSlot :card="item" :collection_stock="collection_stock.o" :current_set_code="current_set_code" :show_option="page_options.show_option_selected.value" :is_extra="(index+pageSliceStart) >= current_set_base_cards_qty" :base_set_total="current_set_base_cards_qty" :extra_set_total="current_set_extra_cards_qty"></CardSlot>
            </v-col>
          </v-row>
        </v-sheet>
      </v-sheet>
      <v-pagination v-if="page_options.card_per_page_option_selected != 4" v-model="current_page" :length="pageCount" :total-visible="isMobile ? 4 : 8"/>
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
        <v-progress-linear height="15" v-model="getProgressForSet" :color="getProgressForSet < 100 ? 'primary' : 'amber-lighten-2' ">
            <template v-slot:default="{ value }">
              <strong>{{ Math.round(value * 10) / 10 }}%</strong>
            </template>
          </v-progress-linear>
      </v-card>
    </v-main>
    <v-main class="intro_message_main" v-if="!current_set || !current_set_base_cards">
      <v-sheet class="intro_message_body rounded-lg" justify="center">
        <img class="title_logo" src="@/assets/collectron-title-logo.png"/>
        <h2 class="intro_title">Welcome to the MTG Collectron</h2>
        <h3 class="intro_title">A visual collection tracker tool for Magic: the Gathering</h3>
        <br>
        <p>To get started, select a set name on the Set Navigation to the left, or open the Tools menu on the right.</p>
        <p>Hover/tap over cards to see the controls and add cards to your collection, or directly import them with the 'Import Cards' tool.</p>
        <br>
        <v-divider/>
        <br>
        <p style="padding:4px; font-size: 13px;">Magic: the Gathering, all card images, symbols and information associated with it, are copyrighted by Wizards of the Coast LLC, and I'm not affiliated with or endorsed by them.</p>
        <p style="padding:4px; font-size: 13px;">Card and set information, data searches, and visual information such as card and set icon pictures, are all sourced from Scryfall and its API. This site is not affiliated with them in any way, but I'm otherwise very grateful for their accessibility.</p>
        <br>
        <p style="padding:4px; font-size: 11px;">version 1.1.0 - last update 26/12/24</p>
        
      </v-sheet>
    </v-main>
    <v-card>
      <v-navigation-drawer app temporary v-model="drawer" elevation="2" :width="isMobile ? '100%' : 300">
        <v-list dense>
          <v-list-item id="column_set_visib_title"><p class="column_header">Set Visibility</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="core" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <label for="check_core" style="display: inline-block;">Core Sets</label>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="expansion" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Expansions</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="masters" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Masters Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="commander" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Commander Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="draft_innovation" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Draft Innovation Sets</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="masterpiece" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Masterpieces</p>
          </v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <input type="checkbox" value="all" v-model="set_types_shown" :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Other Sets</p>
          </v-list-item>
        </v-list>
        <v-list-item><p class="column_header">Search for Set</p></v-list-item>
        <v-list-item><v-text-field v-model="set_search" prepend-inner-icon="mdi-magnify" variant="outlined" density="compact"/></v-list-item>
        <v-list-item><p class="column_header">List of Sets</p></v-list-item>
        <v-list-item v-for="set in set_list"> <div @click="select_set(set)" v-show="set['digital'] == false && (set_types_shown.includes(set['set_type']) || (set_types_shown.includes('all') && !['core','expansion','commander','masters','draft_innovation','masterpiece'].includes(set['set_type']))) && (set_search == '' || set['name'].toLowerCase().includes(set_search.toLowerCase()) || set.code == set_search.toLowerCase()) && ((new Date(new Date().setDate(new Date().getDate()+7))).toISOString().substring(0,10) >= set.released_at)" class="set_list_element" :class="{'set_list_element_selected_light': set.code == current_set_code && !page_options.dark_mode, 'set_list_element_selected_dark': set.code == current_set_code && page_options.dark_mode, 'tertiary_hover_light': !page_options.dark_mode, 'tertiary_hover_dark': page_options.dark_mode }" >
          <v-img :src="set.icon_svg_uri" class="set_logo" :class="{ set_logo_white : page_options.dark_mode }" width="18px" height="18px"/>
          <p class="set_list_name">{{ set.name }}</p>
        </div> </v-list-item>
      </v-navigation-drawer>
    </v-card>
    <v-card>
      <v-navigation-drawer app temporary v-model="settings" elevation="2" location="right" :width="isMobile ? '100%' : 300">
        <v-list dense>
          <v-list-item><p class="column_header">User Preferences</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <v-switch v-model="page_options.dark_mode" label="Toggle Dark Mode" hide-details="true" style="margin-left:10px;" color="primary"/>
            <v-select v-model="page_options.full_set_option_selected" label="Full Set Definition" :items="full_set_options" return-object>
              <v-tooltip activator="parent" location="bottom">Defines the objective considered for the progress bars and 'full set' message displays for each set</v-tooltip>
            </v-select>
          </v-list-item>
          <v-divider/>
          <v-list-item><p class="column_header">Collection Functions</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <v-btn @click="card_finder_window_active = true" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">Card Finder</v-btn>
            <v-btn @click="decklist_finder_window_active = true" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">Decklist Finder</v-btn>
            <v-btn @click="import_window_active = true" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">Import Cards</v-btn>
            <v-btn @click="exportCollection" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">Export Collection</v-btn>
            <p v-show="clicks_to_clear >= 1">WARNING: this will delete ALL saved data. You must click the button {{ 10 - clicks_to_clear }} more times to complete the action.</p>
            <v-btn @click="clear_all_data()" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">Clear ALL card data</v-btn>
          </v-list-item>
          <v-divider/>
          <v-list-item><p class="column_header">Information</p></v-list-item>
          <v-list-item style="display: inline-block; width:100%;">
            <v-btn @click="about_window_active = true" class="side_drawer_button" :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable" variant="outlined">About the Collectron</v-btn>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>
    </v-card>
  </v-app>
</template>

<script setup>
import { onMounted, ref, watch, reactive, computed } from 'vue'
import { useTheme, useDisplay } from 'vuetify'
import CardSlot from './CardSlot.vue'
import sets_json from './scryfall_data/sets.json'
import { unref } from 'vue';

// -------------------- THEME BLOCK --------------------------- //

const lightTheme = {
  dark: false,
  colors: {
    background: '#FFFFFF',
    surface: '#FFFFFF',
    'surface-bright': '#FFFFFF',
    'surface-light': '#EEEEEE',
    'surface-variant': '#424242',
    'on-surface-variant': '#EEEEEE',
    primary: '#FE4E6A',
    // primary: '#EC407A',
    'primary-darken-1': '#D81B60',
    secondary: '#FF899C',
    'secondary-darken-1': '#E53F59',
    tertiary: '#FFC0CA',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
  },
  variables: {
    'border-color': '#000000',
    'border-opacity': 0.12,
    'high-emphasis-opacity': 0.87,
    'medium-emphasis-opacity': 0.60,
    'disabled-opacity': 0.38,
    'idle-opacity': 0.04,
    'hover-opacity': 0.04,
    'focus-opacity': 0.12,
    'selected-opacity': 0.08,
    'activated-opacity': 0.12,
    'pressed-opacity': 0.12,
    'dragged-opacity': 0.08,
    'theme-kbd': '#212529',
    'theme-on-kbd': '#FFFFFF',
    'theme-code': '#F5F5F5',
    'theme-on-code': '#000000',
  }
}

const darkTheme = {
  dark: true,
  colors: {
    background: '#444444',
    surface: '#484848',
    'surface-bright': '#FFFFFF',
    'surface-light': '#EEEEEE',
    'surface-variant': '#424242',
    'on-surface-variant': '#EEEEEE',
    primary: '#66A0D8',
    'primary-darken-1': '#3E789F',
    secondary: '#9EC5F7',
    'secondary-darken-1': '#80a5d3',
    tertiary: '#BDD8FB',
    error: '#B00020',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
  },
  variables: {
    'border-color': '#000000',
    'border-opacity': 0.12,
    'high-emphasis-opacity': 0.87,
    'medium-emphasis-opacity': 0.60,
    'disabled-opacity': 0.38,
    'idle-opacity': 0.04,
    'hover-opacity': 0.04,
    'focus-opacity': 0.12,
    'selected-opacity': 0.08,
    'activated-opacity': 0.12,
    'pressed-opacity': 0.12,
    'dragged-opacity': 0.08,
    'theme-kbd': '#212529',
    'theme-on-kbd': '#FFFFFF',
    'theme-code': '#F5F5F5',
    'theme-on-code': '#000000',
  }
}

const theme = useTheme()
const display = useDisplay()

theme.themes.value.light = lightTheme
theme.themes.value.dark = darkTheme

// toggles between light and dark mode for the color scheme
function toggleDarkMode (bool) {
  theme.global.name.value = bool ? 'dark' : 'light'
  // console.log(theme)
  // theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}


// ------------------------------------------------------------ //

var drawer = ref(true)    // signals the set navigation drawer is open
var settings = ref(false) // signals the settings menu is open
var loading = ref(false)  // signals the loading circle is visible
var card_finder_window_active = ref(false)              // signals the card search dialog is visible
var decklist_finder_window_active = ref(false)          // signals the decklist finder dialog is visible
var decklist_finder_results_window_active = ref(false)  // signals the decklist finder results dialog is visible
var import_window_active = ref(false)   // signals the import dialog is visible
var import_results_active = ref(false)  // signals the import dialog results are visible
var export_window_active = ref(false)   // signals the import dialog is visible
var about_window_active = ref(false)    // signals the import dialog is visible

var card_finder_text = ref('')
var card_finder_results = ref([])

var decklist_finder_searchlist = ref([])          // the list of cards passed to be searched on decklist search, as objects
var decklist_finder_priority = ref('oldest')      // fetch priority of the searched cards ('oldest' or 'newest')
var decklist_finder_text = ''                     // textbox contents of the decklist search
var decklist_finder_results = ref([])             // all of the results returned for a decklist search, dupes included
var decklist_finder_results_processed = ref([])   // the currently filtered decklist search results

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
  card_per_page_option_selected: 1,
  dark_mode: false,
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
  {value: 2, title: 'Base set only'},
  {value: 3, title: 'At least one version of each card name'}
]

// -------------------------------------------------------------------------------------------------- //

onMounted(() => {
  // // localStorage.removeItem('collection_stock')
  set_list.value = sets_json['data']

  // start the set navigation closed on mobile
  if(unref(display.mobile)){
    drawer.value = false
  }
  
  // get the list of set options from local storage
  const set_options = JSON.parse(localStorage.getItem('set_options'))
  if(set_options)  {  set_types_shown.value = set_options  }
  get_preferences_from_storage()
  
  const local_stock = JSON.parse(localStorage.getItem('collection_stock'))
  if(local_stock) { collection_stock.o = local_stock }

  backfill_set_release_date()

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
  toggleDarkMode(page_options.dark_mode)
  current_page.value = 1
})
watch(card_search, v => {
  current_page.value = 1
})
watch(card_finder_text, v => {
  if(v.length >= 3){
    findCardsInCollection()
  } else {
    card_finder_results.value = []
  }
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

  // the following blocks are safeguards and ideally are never called in production use
  if(collection_stock.o[set.code] && !collection_stock.o[set.code].foils_owned) {
    collection_stock.o[set.code].foils_owned = tally_foils(set.code)
  }
  if(collection_stock.o[set.code] && !collection_stock.o[set.code].released_at) {
    collection_stock.o[set.code].released_at = set.released_at
  }
  
  // for any sets with traditional boosters and structure, we get their base cards and extra cards separately
  if(['core','draft_innovation','masters','expansion','starter'].includes(set.set_type)) {
    try {
      current_set_base_cards.value = await get_set_base_cards(set.code)
      current_set_base_cards_qty = current_set_base_cards.value.length
    }
    catch {
      current_set_base_cards.value = []
    }
      
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
  if(set.code in collection_stock.o){
    collection_stock.o[set.code].base_set_total = current_set_base_cards_qty
    collection_stock.o[set.code].extra_set_total = current_set_extra_cards_qty ? current_set_extra_cards_qty : 0
  }

  // console.log("current set data:",current_set_base_cards.value)

  // close the set navigation tab after selecting the set, if on mobile
  if(unref(display.mobile)) {
    drawer.value = false
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
    page_options.dark_mode = stored_options.dark_mode
  } else {
    const user_options = {
      full_set_option_selected: {value: 1, title: 'Every single card, variants included'},
      card_per_page_option_selected: {value: 2, title: 60},
    }
    page_options.full_set_option_selected = user_options.full_set_option_selected
    page_options.card_per_page_option_selected = user_options.card_per_page_option_selected
    page_options.dark_mode = false

    localStorage.setItem('stored_options',JSON.stringify(page_options))
  }
}

// get all base card information for the selected set
async function get_set_base_cards(set_code) {
  var total_data = []
  var has_more = false
  // var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset&unique=cards&as=grid&order=name"
  var fetch_url = "https://api.scryfall.com/cards/search?q=%28game%3Apaper%29+set%3A"+set_code+"+unique%3Aprints+order%3Aset+-is%3Aboosterfun+is%3Abooster+-otag:melded&unique=cards"
  
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
  var fetch_url = "https://api.scryfall.com/cards/search?order=set&q=set%3A"+set_code+"+%28is%3Apromo+or+is%3Abooster_fun+or+is%3Ajumpstart%29+game%3Apaper+unique%3Aprints&unique=cards"
  
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

// returns a list of every card in the collection that matches the typed string
function findCardsInCollection(){
  const cardName = card_finder_text.value.toLowerCase()
  var cardList = []
  for(var set in collection_stock.o){
    for(var card in collection_stock.o[set].cards) {
      if(card.toLowerCase().includes(cardName))
      {
        for(var cardVer in collection_stock.o[set].cards[card])
        {
          const tagSquare = collection_stock.o[set].cards[card][cardVer].tag_square ? '■' : ''
          const tagTriangle = collection_stock.o[set].cards[card][cardVer].tag_triangle ? '▲' : ''
          const tagCircle = collection_stock.o[set].cards[card][cardVer].tag_circle ? '⚫︎' : ''
          const tagCross = collection_stock.o[set].cards[card][cardVer].tag_cross ? '✖' : ''
          const formattedCardName = card + ' (' + set.toUpperCase() + '-' + cardVer + ') ' + tagSquare + tagTriangle + tagCircle + tagCross
          cardList.push({cardName:card, cardSet:set, formattedCardName:formattedCardName})
        }
      }
    }
  }
  cardList.sort(compareCards)
  card_finder_results.value = cardList
}

// returns a list of every printing of a specific card name in your collection, with optional parameters
function findSpecificCardInCollection(cardName,setName,number){
  try {
    cardName = cardName
    var cardList = []
    if(setName) {
      if(setName in collection_stock.o && cardName in collection_stock.o[setName].cards) {
        for(var cardVer in collection_stock.o[setName].cards[cardName])
        {
          const tagSquare = collection_stock.o[setName].cards[cardName][cardVer].tag_square ? '■' : ''
          const tagTriangle = collection_stock.o[setName].cards[cardName][cardVer].tag_triangle ? '▲' : ''
          const tagCircle = collection_stock.o[setName].cards[cardName][cardVer].tag_circle ? '⚫︎' : ''
          const tagCross = collection_stock.o[setName].cards[cardName][cardVer].tag_cross ? '✖' : ''
          const cardAmount = collection_stock.o[setName].cards[cardName][cardVer].count
          const formattedCardName = cardAmount + 'x ' + cardName + ' (' + setName.toUpperCase() + '-' + cardVer + ') ' + tagSquare + tagTriangle + tagCircle + tagCross
          if(!number || cardVer == number){
            cardList.push(
              {cardName:cardName, 
                cardSet:setName, 
                formattedCardName:formattedCardName, 
                releaseDate:collection_stock.o[setName].released_at, 
                amount:cardAmount})
          }
        }
      }
    } else {
      for(var set in collection_stock.o){
        for(var card in collection_stock.o[set].cards) {
          if(card == cardName)
          {
            for(var cardVer in collection_stock.o[set].cards[card])
            {
              const tagSquare = collection_stock.o[set].cards[card][cardVer].tag_square ? '■' : ''
              const tagTriangle = collection_stock.o[set].cards[card][cardVer].tag_triangle ? '▲' : ''
              const tagCircle = collection_stock.o[set].cards[card][cardVer].tag_circle ? '⚫︎' : ''
              const tagCross = collection_stock.o[set].cards[card][cardVer].tag_cross ? '✖' : ''
              const cardAmount = collection_stock.o[set].cards[card][cardVer].count
              const formattedCardName = card + ' (' + set.toUpperCase() + '-' + cardVer + ') ' + tagSquare + tagTriangle + tagCircle + tagCross
              cardList.push(
                {cardName:card, 
                  cardSet:set, 
                  formattedCardName:formattedCardName, 
                  releaseDate:collection_stock.o[set].released_at, 
                  amount:cardAmount})
            }
          }
        }
      }
    }
    
    return cardList.sort(function(a,b){
      return new Date(a.releaseDate) - new Date(b.releaseDate)
    })
  } catch (err){
    console.log("An error has occurred on findSpecificCardInCollection:",err)
  }
}

// upon selecting a card on the card finder, go to the set selected and search for the typed card
async function goToFoundCard(cardName, cardSet){
  try {
    const set = set_list.value.find(e => e.code.toLowerCase() == cardSet.toLowerCase())
    await select_set(set)
    card_finder_window_active.value = false
    card_finder_text.value = ''
    card_finder_results.value = []
    card_search.value = cardName
    if(isMobile){   // on mobile we hide the settings window again to get it out of the way
      settings.value = false
    }
  }
  catch(err){
    console.log("An error has occurred on goToFoundCard:",err)
  }
}

// search for list of cards passed, according to the priority set
async function perform_decklist_finder_search() {
  loading.value = true
  import_results_active.value = false
  var cardList = []

  // first, we split the list of cards to search, one per line
  var split_cards = decklist_finder_text.split('\n')

  // then, we iterate through the list
  for(let i = 0; i < split_cards.length; i++) {
    try {
      // for each card, we set up a return object to later use to push the card
      var card = {'name': '', 'amount': 0, 'set': '', 'collector_number': 0, 'foil': false}

      // first we split the card by ' (' (note the space), the first half is the quantity and card name, the second half is the set name, collector number and modifiers
      const card_elements = split_cards[i].split(' (')
      // then we split the first part in two at the first space, and grab the first element as the amount
      const amount = card_elements[0].split(' ',1)[0]
      // if the first element is not a number, it's an error
      if(parseInt(amount)) {
        card.amount = amount
      } else {
        throw EvalError()
      }
      // the remaining elements of the first part should be the card name
      card.name = card_elements[0].substring(card_elements[0].indexOf(' ')+1)

      // if there was no parentheses (and thus no identifying information for the card) we just skip that part
      if(card_elements.length > 1) {
        // the second part, past the first parentheses, is further split by the second parentheses; the first element is the set, the second (if exists) may indicate foil
        const second_part = card_elements[1].split(') ')  // TODO: string that ends in ')' isn't split properly due to this
        const third_part = second_part[1]?.split(' ')
        card.set = second_part[0].toLowerCase()
        if(third_part && parseInt(third_part[0])) {
          card.collector_number = third_part[0]
        } else {
          card.collector_number = 0
        }
        if(third_part && third_part.length >= 2 && ['*F*','*E*'].includes(third_part[1]))
        {
          card.foil = true
        }
      }

      // push the card element above into our searchlist, to be used later for cleanup/skip purposes
      decklist_finder_searchlist.value.push(card)

      // return a list of all instances of the named card in your collection, optionally narrowing by set and/or number
      let cardsFound = findSpecificCardInCollection(card.name, card.set != '' ? card.set : undefined, card.collector_number != 0 ? card.collector_number : undefined)
      // if search priority is newest cards first, we revert the (normally oldest to newest) array
      if(decklist_finder_priority.value == "newest") cardsFound = cardsFound.reverse()
      // add all of the prints found to the search results pile
      decklist_finder_results.value = decklist_finder_results.value.concat(cardsFound)

      // we grab cards from the returned list until we hit the amount specified
      cardList = cardList.concat(get_enough_cards_from_decklist_filter_results(cardsFound,card.amount))
    }
    catch (e){
      console.log("Error: ",e)
    }
  }
  console.log("decklist_finder_searchlist.value", decklist_finder_searchlist.value)
  
  decklist_finder_results_processed.value = cardList.sort(function(a,b){
      return new Date(a.releaseDate) - new Date(b.releaseDate)
    })
  decklist_finder_results_window_active.value = true
  loading.value = false
}

// decklist filter: for each card we are looking for, return cards from the results list until you have enough of each passed
function get_enough_cards_from_decklist_filter_results(cards,amount){
  let totalCards = 0, cardList = []
  for(var elem in cards) {
    // edit the amount to declare the amount of it we're taking
    cards[elem].amount = Math.min(cards[elem].amount,(amount - totalCards))
    cardList.push(cards[elem])
    
    totalCards += cards[elem].amount
    if(totalCards >= amount)
      return cardList
  }
}

// remove the passed card from the list of filtered cards displayed for a decklist finder search
function mark_decklist_card_as_done(card){
  try {
    console.log("card",card)
    decklist_finder_results_processed.value = decklist_finder_results_processed.value.filter(elem => elem != card)
    const ind = decklist_finder_searchlist.value.findIndex(item => item.name == card.cardName)
    console.log("ind",ind)
    decklist_finder_searchlist.value[ind].amount -= card.amount
    if(decklist_finder_searchlist.value[ind].amount <= 0){
      decklist_finder_searchlist.value.splice(ind,1)
    }
    console.log("decklist_finder_searchlist.value",decklist_finder_searchlist.value)
  } catch(err) {
    console.log(err)
  }
}

// attempts to skip the passed card, putting the next available printing
function skip_decklist_card(card){
  try {
    const amt = card.amountx
    // find the removed card in the mother array
    const ind = decklist_finder_results.value.indexOf()
  } catch(err) {
    console.log(err)
  }
}

// parse and import list of cards on the text box
async function import_cards() {
  loading.value = true
  import_results_active.value = false

  if(import_syntax.value == 'moxfield') {
    await import_from_moxfield()
  }
  else if(import_syntax.value == 'native') {
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
      // for each card, we set up a return object to later use to push the card
      var card = {'name': '', 'amount': 0, 'set': '', 'collector_number': 0, 'foil': false}

      // first we split the card by ' (' (note the space), the first half is the quantity and card name, the second half is the set name, collector number and modifiers
      const card_elements = split_cards[i].split(' (')
      // then we split the first part in two at the first space, and grab the first element as the amount
      const amount = card_elements[0].split(' ',1)[0]
      // if the first element is not a number, it's an error
      if(parseInt(amount)) {
        card.amount = amount
      } else {
        throw EvalError()
      }
      // the remaining elements of the first part should be the card name
      card.name = card_elements[0].substring(card_elements[0].indexOf(' ')+1)
      // console.log('card.name',card.name)

      // the second part, past the first parentheses, is further split by the second parentheses; the first element is the set, the second (if exists) may indicate foil
      const second_part = card_elements[1].split(') ')
      const third_part = second_part[1]?.split(' ')
      card.set = second_part[0].toLowerCase()
      if(parseInt(third_part[0])) {
        card.collector_number = third_part[0]
      } else {
        throw EvalError()
      }
      if(third_part.length >= 2 && ['*F*','*E*'].includes(third_part[1]))
      {
        card.foil = true
        // console.log('card.foil = true')
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
  var error_list = ''
  try {
    const imported_data = JSON.parse(import_text)
    import_text = ''

    collection_stock.o = imported_data
  }
  catch (e){
    error_list = e
    console.log('error:',e)
  }
  // we consider the import a success if there is no error listed
  import_success = (error_list == '')
  import_errors.value = error_list
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
  await sleep(100);

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
      extra_set_total: 0,
      released_at: response_data[0].released_at
    }
    collection_stock.o[card.set] = new_set
  }
  
  // next, we check the existing card stock for copies; if yes, we add to the count; if not, we create a new card template for this card
  if(card.name in collection_stock.o[card.set].cards){
    if(card.collector_number in collection_stock.o[card.set].cards[card.name])
    {
      collection_stock.o[card.set].cards[card.name][card.collector_number].count+= parseInt(card.amount)
      if(card.foil) {
        collection_stock.o[card.set].cards[card.name][card.collector_number].foil = true
      }
    }
    else
    {
      collection_stock.o[card.set].cards[card.name][card.collector_number] = {
        count: parseInt(card.amount),
        foil: card.foil
      }
      
      // if the card matches the first print listed, it's very likely the base set version, unless it's a basic land, token, or card from those weird sets with multiple prints
      if(card.collector_number == response_data[0].collector_number || response_data[0].type_line.toLowerCase().includes('basic') || response_data[0].type_line.toLowerCase().includes('token') || card.set in ['fem','hml','all']) {
        collection_stock.o[card.set].base_set_owned++
      } else {
        collection_stock.o[card.set].extra_owned++
      }
    }
  } else {
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
    // console.log("is extra?",card.collector_number != response_data[0].collector_number)
    if(card.collector_number == response_data[0].collector_number || response_data[0].type_line.toLowerCase().includes('basic') || response_data[0].type_line.toLowerCase().includes('token') || card.set in ['fem','hml','all']) {
      collection_stock.o[card.set].base_set_owned++
    } else {
      collection_stock.o[card.set].extra_owned++
    }
  }
}

// for backfilling during dev, will be obsolete for new users
async function backfill_set_release_date()
{
  try {
    for(var set in collection_stock.o){
      // if the set in question doesn't have a value set for released_at, we will query the sets api and get said value
      if(!collection_stock.o[set].released_at){
        loading.value = true
        console.log("Set "+set+" missing released_at.")
        // scryfall fetch for the set, to get the release date
        var fetch_url = 'https://api.scryfall.com/sets/'+set
        const response = await fetch(fetch_url);
        const response_contents = await response.json();
        await sleep(100);
        collection_stock.o[set].released_at = response_contents.released_at
      }
    }
  } catch(err) {
    console.log(err)
  } finally {
    loading.value = false
  }
}

// this counts the foils for a set and adds the variable; for backfilling, should be eventually obsolete
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
    // console.log("collection_stock.o[current_set_code.value].base_set_owned",collection_stock.o[current_set_code.value].base_set_owned)
    // console.log("collection_stock.o[current_set_code.value].base_set_total",collection_stock.o[current_set_code.value].base_set_total)
    // console.log("collection_stock.o[current_set_code.value].extra_owned",collection_stock.o[current_set_code.value].extra_owned)
    // console.log("collection_stock.o[current_set_code.value].extra_set_total",collection_stock.o[current_set_code.value].extra_set_total)
    switch(page_options.full_set_option_selected.value) {
      case 1: // every single card, variants included
        // console.log("getProgressForSet, switch 1, value",((collection_stock.o[current_set_code.value].base_set_owned + collection_stock.o[current_set_code.value].extra_owned) / (collection_stock.o[current_set_code.value].base_set_total + collection_stock.o[current_set_code.value].extra_set_total))*100)
        return ((collection_stock.o[current_set_code.value].base_set_owned + collection_stock.o[current_set_code.value].extra_owned) / (collection_stock.o[current_set_code.value].base_set_total + collection_stock.o[current_set_code.value].extra_set_total))*100
      case 2: // base set only
        // console.log("getProgressForSet, switch 2, value", (collection_stock.o[current_set_code.value].base_set_owned / collection_stock.o[current_set_code.value].base_set_total)*100)
        return (collection_stock.o[current_set_code.value].base_set_owned / collection_stock.o[current_set_code.value].base_set_total)*100
      case 3: // at least one version of every card
        // console.log("getProgressForSet, switch 3, value",((collection_stock.o[current_set_code.value].commons + collection_stock.o[current_set_code.value].uncommons + collection_stock.o[current_set_code.value].rares + collection_stock.o[current_set_code.value].mythics) / (current_set_commons.value + current_set_uncommons.value +current_set_rares.value + current_set_mythics.value))*100)
        console.log("collection_stock.o[current_set_code.value]",collection_stock.o[current_set_code.value])
        return ((collection_stock.o[current_set_code.value].commons + collection_stock.o[current_set_code.value].uncommons + collection_stock.o[current_set_code.value].rares + collection_stock.o[current_set_code.value].mythics) / (current_set_commons.value + current_set_uncommons.value +current_set_rares.value + current_set_mythics.value))*100
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
const isMobile = computed(() => {
  return unref(display.mobile)
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

function compareCards(a,b){
  if ( a.cardName < b.cardName ){
    return -1;
  }
  if ( a.cardName > b.cardName ){
    return 1;
  }
  return 0;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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
.title_logo {
  width: 80%;
  max-width: 320px;
  display: inline-block;
  margin-left: auto;
  margin-right: auto;
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
  border-radius: 4px;
}
.set_list_element:hover {
  cursor:pointer;
}
.set_list_element_selected_light {
  background-color: #FF899C;
  font-weight: bold;
}
.set_list_element_selected_dark {
  background-color:#9EC5F7;
  font-weight: bold;
}
.set_logo, .set_check {
  display: inline-block;
  margin: 2px 5px;
  accent-color: #FF899C;
}
.set_logo_white {
  filter: invert(100)
}
.set_check_dark {
  display: inline-block;
  margin: 2px 5px;
  accent-color: #9EC5F7;
}
.set_list_name {
  display: inline-block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}
.card_list_main {
  margin: 0 auto;
  width: 100%;
  max-width: 800px;
}
.card_list_body {
  width: 100%;
  margin-top: 30px;
  display: inline-block;
  text-align: center;
}
.intro_message_main {
  margin: 0 auto;
  width: 100%;
  max-width: 800px;
}
.intro_message_body {
  width: 100%;
  max-width: 1200px;
  margin-top: 50px;
  padding: 0 3%;
  display: inline-block;
  text-align: center;
}
.intro_title {
  /* font-family: "Lucida Console", "Courier New", monospace; */
  font-family: 'Aoboshi One', "Lucida Console", "Courier New", monospace;
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
  right: 80px;
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
  width: 260px;
}
.tertiary_hover_light:hover {
  background-color: #FFC0CA;
}
.tertiary_hover_dark:hover {
  background-color: #BDD8FB;
  color: black;
}
.card_finder_window {
  width: 500px;
  height: 100%;
  text-align: center;
}
.card_finder_results_list {
  height: 100%;
  max-height: 400px;
  overflow-y: auto;
}
.card_finder_results_element:hover {
  background-color: #F8BBD0;
}
.decklist_finder_results_window {
  width: 500px;
  height: 100%;
  text-align: left;
}
.decklist_finder_results_list_item {
  display: inline-block;
  width: 100%;
  margin-bottom: -3px;
}
.decklist_finder_results_text {
  cursor: default;
  width: auto;
  display: inline;
  margin-left: 10px;
}
.import_window {
  width: 100%;
  max-width: 500px;
  height: 330px;
  text-align: center;
}
.import_results_window {
  width: 100%;
  min-width: 250px;
  max-width: 500px;
  height: 100%;
  min-height: 250px;
  max-height: 600px;
  text-align: center;
  padding: 0 20px;
}
.export_window {
  width: 100%;
  max-width: 500px;
  height: 300px;
  text-align: center;
}
.about_window {
  width: 95%;
  max-width: 600px;
  height: 100%;
  text-align: center;
}
.import_window_header {
  width: 100%;
  height: 70px;
}
.import_text_field {
  width: 450px;
  max-width: 90%;
  height: 150px;
  display: inline-block;
  margin-top: 10px;
}
.card_finder_text_field {
  padding: 10px 20px;
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
/* @media screen and (min-width: 1530px) {
  .card_list_body {
    width: 900px;
  }
} */
/* @media screen and (max-width: 1529px) {
  .card_list_body {
    width: 80%;
  }
} */
@media screen and (max-width: 960px) {
  .card_list_body {
    width: 95%;
    margin: 0 auto;
  }
}
</style>
