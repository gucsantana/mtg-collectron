<template>
  <Login v-if="!authChecking && !isAuthenticated" :initial-error="authError" @authenticated="handleAuthenticated" />
  <v-app v-else-if="authChecking" class="align-center justify-center">
    <v-progress-circular color="primary" indeterminate size="64" />
  </v-app>
  <template v-else>
    <v-app>
      <v-alert v-if="authError" type="error" closable class="auth_error" @click:close="authError = ''">
        {{ authError }}
      </v-alert>
      <v-overlay persistent :model-value="loading" class="align-center justify-center">
        <div class="text-center pa-4">
          <v-progress-circular color="primary" indeterminate size="64" />
          <p v-if="import_status_message" class="import_status_message mt-4">
            {{ import_status_message }}
          </p>
        </div>
      </v-overlay>
      <v-overlay persistent :model-value="loading_bar" class="align-center justify-center">
        <v-progress-linear v-model="loading_bar_fill" height="20" style="width:400px;" color="primary" rounded />
      </v-overlay>
      <DecklistFinder v-if="isDecklistFinderPage" :user-id="userId" :dark-mode="page_options.dark_mode"
        :csrf-token="csrf_token" :set-list="set_list"
        @back="navigateToMainPage" @open-settings="settings = !settings" />
      <v-overlay :model-value="card_finder_window_active" @afterLeave="card_finder_window_active = false"
        class="align-center justify-center">
        <v-card class="card_finder_window">
          <v-card-item>
            <v-row class="import_window_header align-center">
              <v-col cols="6">
                <h2>Card Finder</h2>
              </v-col>
              <v-spacer />
              <v-col cols="1">
                <v-tooltip text="/n" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary" />
                  </template>
                  <p>Searches your card collection for matches with the typed card name</p>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-card-item>
          <v-divider />
          <v-text-field v-model="card_finder_text" label="Search" autofocus prepend-inner-icon="mdi-magnify"
            class="card_finder_text_field" variant="outlined" />
          <!-- <v-card class="align-right">
          <input type="checkbox" value="tag_square_marked" v-model="tags_selected" class="tag_check">
          <label for="tag_square_marked" style="display: inline-block;">■</label>
        </v-card> -->
          <v-list nav class="card_finder_results_list align-left" v-show="card_finder_results.length > 0">
            <v-list-item v-for="card in card_finder_results" :title="card.formattedCardName"
              @click="goToFoundCard(card.cardName, card.cardSet)"
              :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" />
          </v-list>
          <v-card-actions>
            <v-spacer />
            <v-col cols="3"><v-btn @click="card_finder_window_active = false; card_finder_text = ''"
                variant="outlined">Close</v-btn></v-col>
          </v-card-actions>
        </v-card>
      </v-overlay>
      <v-overlay :model-value="import_window_active" @afterLeave="import_window_active = false"
        class="align-center justify-center">
        <v-card class="import_window">
          <v-card-item>
            <v-row class="import_window_header align-center">
              <v-col cols="6">
                <h2>Import Cards</h2>
              </v-col>
              <v-spacer />
              <v-col cols="1">
                <v-tooltip text="/n" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-icon :="props" icon="mdi-help-box" size="x-large" color="primary" />
                  </template>
                  <p>'Moxfield Syntax' uses the Moxfield syntax, one card per line</p>
                  <p class="mb-0">e.g. "1 Loran's Escape (BRO) *F*"</p>
                  <p class="mb-0">'Exported File' uses the CSV backup file exported by the 'Export Collection' button
                  </p>
                </v-tooltip>
              </v-col>
            </v-row>
          </v-card-item>
          <v-divider />
          <div class="import_window_content">
            <v-radio-group inline v-model="import_syntax" density="compact" hide-details class="import_syntax_selector"
              @update:model-value="import_replace_confirmed = false">
              <v-radio color="primary" label="Moxfield Syntax" value="moxfield" />
              <v-radio color="primary" label="Exported File" value="native" />
            </v-radio-group>
            <v-textarea v-model="import_text" v-if="import_syntax == 'moxfield'" autofocus class="import_text_field"
              variant="outlined"/>
            <v-file-input accept="text/csv" @change="loadImportFileToMemory" clearable label="Upload CSV file"
              v-if="import_syntax == 'native'" class="import_file_field" variant="outlined"></v-file-input>
            <div v-if="import_syntax == 'native'" class="import_action_options">
              <v-radio-group v-model="import_action" density="compact" hide-details class="import_action_selector"
                @update:model-value="import_replace_confirmed = false">
                <v-radio color="primary" label="Add cards from CSV to collection" value="add" />
                <v-radio color="primary" label="Replace collection with cards from CSV" value="replace" />
              </v-radio-group>
              <v-checkbox v-if="import_action == 'replace'" v-model="import_replace_confirmed" color="primary"
                label="Confirm" density="compact" hide-details class="import_replace_confirmation" />
              <v-text-field v-model="import_password" label="Password" type="password" autocomplete="current-password"
                required variant="outlined" density="compact" hide-details class="import_password_field" />
            </div>
          </div>
          <v-card-actions class="import_window_actions">
            <v-spacer />
            <v-btn @click="import_cards" variant="outlined"
              :disabled="import_syntax == 'native' && (!import_password.trim() || (import_action == 'replace' && !import_replace_confirmed))">
              Import
            </v-btn>
            <v-btn @click="import_window_active = false" variant="outlined">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-overlay>
      <v-overlay :model-value="import_results_active" @afterLeave="import_results_active = false"
        class="align-center justify-center">
        <v-card class="import_results_window">
          <v-card-item>
            <h2 v-show="import_success == true">Import Success</h2>
            <h2 v-show="import_success == false">Import Failure</h2>
          </v-card-item>
          <v-divider />
          <br />
          <p v-show="import_card_total > 0">Imported {{ import_card_total }} unique cards.</p>
          <p v-show="import_syntax == 'native' && import_success">{{ import_result_message }}</p>
          <br />
          <p v-show="import_errors.length > 0 && import_syntax == 'moxfield'">The following lines could not be imported:
          </p>
          <br v-show="import_errors.length > 0 && import_syntax == 'moxfield'" />
          <p v-show="import_errors">{{ import_errors }}</p>
        </v-card>
      </v-overlay>
      <v-overlay :model-value="housekeeping_window_active" @afterLeave="housekeeping_window_active = false"
        class="align-center justify-center">
        <v-card class="housekeeping_window">
          <v-card-item>
            <v-row class="housekeeping_window_header align-center">
              <v-col cols="6">
                <h2>Housekeeping Tasks</h2>
              </v-col>
              <v-spacer />
            </v-row>
          </v-card-item>
          <v-divider />
          <v-card-item class="housekeeping_window_footer">
            <p>Recalculate card counts and percentages for all sets. This takes a while, use only if you notice some
              values
              are wrong.</p>
            <v-btn @click="tidy_up_collection" class="side_drawer_button"
              :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
              variant="outlined">
              Tidy Up Collection</v-btn>
            <v-divider />
            <p v-show="clicks_to_clear >= 1">WARNING: this will delete ALL saved data. You must click the button {{ 10 -
              clicks_to_clear }} more times to complete the action.</p>
            <v-btn @click="clear_all_data()" class="side_drawer_button"
              :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
              variant="outlined">
              Clear ALL card data</v-btn>
          </v-card-item>
          <v-row class="house mt-auto">
            <v-spacer />
            <v-col cols="3"><v-btn @click="housekeeping_window_active = false">Close</v-btn></v-col>
          </v-row>
        </v-card>
      </v-overlay>
      <v-overlay :model-value="export_window_active" @afterLeave="export_window_active = false"
        class="align-center justify-center">
        <v-card class="export_window">
          <v-card-item>
            <v-row class="import_window_header align-center">
              <v-col cols="6">
                <h2>Export Collection</h2>
              </v-col>
            </v-row>
          </v-card-item>
          <v-divider />
          <p>Exports card and set information as a CSV file.</p>
          <p class="mb-0">Card information appears first, followed by set information.</p>
          <v-card-actions style="margin-top:20px;">
            <v-spacer />
            <v-col cols="3"><v-btn @click="saveCollectionFile" variant="outlined">Save CSV</v-btn></v-col>
            <v-col cols="2"><v-btn @click="export_window_active = false" variant="outlined">Close</v-btn></v-col>
          </v-card-actions>
        </v-card>
      </v-overlay>
      <v-overlay id="about_window" :model-value="about_window_active" @afterLeave="about_window_active = false"
        class="align-center justify-center">
        <v-card class="about_window">
          <v-card-item>
            <h2>About the Collectron</h2>
          </v-card-item>
          <v-divider />
          <p style="padding:4px 20px; font-size: 13px;">This website has been built from scratch and maintained by Guilherme
            Santana, tested on Chrome/Firefox desktop and Firefox mobile.</p>
          <p style="padding:4px 20px; font-size: 13px;">Tech stack: JavaScript with Vue/Vuetify for the front-end, Java Spring Boot backend, 
            MySQL database, all hosted on a self-managed AWS stack. Copilot was used to speed up development, but the design and features are entirely my own.</p>
          <p style="padding:4px 20px; font-size: 13px;">The site is presented as-is - consider it an ongoing beta - and I
            make no guarantee about its accuracy, continued functionality, or backwards compatibility of new functions, but I
            hope you enjoy using it nonetheless.</p>
          <br />
          <v-divider/>
          <p style="padding:4px 20px; font-size: 13px;">Magic: the Gathering, all card images, symbols and information
            associated with it, are copyrighted by Wizards of the Coast LLC, and I'm not affiliated with or endorsed by them.</p>
          <p style="padding:4px 20px; font-size: 13px;">Card and set information, data searches, and visual information such
            as card and set icon pictures, are all sourced from Scryfall and its API. This site is not affiliated with them
            in any way, but I'm otherwise very grateful for their accessibility.</p>
          <br />
          <v-divider/>
          <v-card-actions style="padding-left:20px;">
            <img class="tech_logos" src="@/assets/js-logo.png" />
            <img class="tech_logos" src="@/assets/vue-logo.png" />
            <img class="tech_logos" src="@/assets/java-logo.png" />
            <img class="tech_logos" src="@/assets/spring-boot-logo.png" />
            <img class="tech_logos" src="@/assets/aws-logo.png" />
            <v-spacer />
            <v-btn @click="about_window_active = false" variant="outlined"
              style="margin-right: 10px; margin-bottom: 10px;">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-overlay>
      <v-snackbar v-model="toast" :timeout="2000">Copied to clipboard!</v-snackbar>
      <v-snackbar v-model="finished_housekeeping" :timeout="2500">Finished cleaning up your collection!</v-snackbar>
      <v-app-bar v-if="!isDecklistFinderPage" color="primary">
        <v-btn @click="drawer = !drawer">
          <v-icon icon="mdi-chevron-right-circle" size="x-large" v-if="!drawer" />
          <v-icon icon="mdi-chevron-left-circle" size="x-large" v-if="drawer" />
          <p style="margin-left: 10px;">Set Navigation</p>
        </v-btn>
        <v-spacer />
        <v-btn @click="settings = !settings">
          <v-icon icon="mdi-menu" size="x-large" />
        </v-btn>
      </v-app-bar>
      <v-main class="card_list_main" v-if="!isDecklistFinderPage && current_set && current_set_base_cards">
        <v-sheet class="card_list_body rounded-lg">
          <v-card id="set_page_title_card" :height="isMobile ? 140 : 100" flat>
            <div>
              <v-img :src="current_set.icon_svg_uri" class="set_logo"
                :class="{ set_logo_white: page_options.dark_mode }" width="30px" height="30px" />
              <p class="set_page_title">{{ current_set.name }} ({{ current_set.code.toUpperCase() }})</p>
            </div>
            <div style="display:inline-block; margin-right: 30px;">
              <p class="set_page_subtitle">Release Date:</p>
              <p class="set_page_subtext">{{ current_set['released_at'] }}</p>
            </div>
            <div style="display:inline-block">
              <p class="set_page_subtitle">Set Type:</p>
              <p class="set_page_subtext">{{ current_set['set_type'].replace('_', ' ') }}</p>
            </div>
          </v-card>
          <v-row>
            <v-col cols="12" sm="3">
              <v-text-field v-model="card_search" label="Card Search" prepend-inner-icon="mdi-magnify"
                variant="outlined" color="primary" density="compact" clearable @click:clear="card_search = ''" />
            </v-col>
            <v-spacer v-show="!isMobile" />
            <v-col cols="12" sm="3">
              <v-select v-model="page_options.card_per_page_option_selected" label="Cards per Page"
                :items="card_per_page_options" return-object density="compact" variant="outlined" />
            </v-col>
          </v-row>
          <v-card class="page_header">
            <v-card class="set_stats_banner" flat>
              <v-row style="height: 70px;" align="center">
                <v-col>
                  <p>Base Set:</p>
                  <p>{{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p>
                </v-col>
                <v-divider vertical />
                <v-col v-if="current_set_extra_cards_qty > 0">
                  <p style="display:inline;">Extra Cards:</p>
                  <v-tooltip text="/n" location="bottom" style="display:inline;">
                    <template v-slot:activator="{ props }">
                      <v-icon :="props" icon="mdi-help-circle" size="medium" color="primary"
                        style="margin-left:10px;" />
                    </template>
                    <p>Showcase frame cards, extended art carts, borderless cards, Buy-a-Box, etc</p>
                  </v-tooltip>
                  <p>{{ current_set_owned_extra_cards }}/{{ current_set_extra_cards_qty }}</p>
                </v-col>
                <v-divider vertical v-if="current_set_extra_cards_qty > 0" />
                <v-col>
                  <p>Grand Total:</p>
                  <p>{{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{
                    current_set_base_cards_qty +current_set_extra_cards_qty }}</p>
                </v-col>
                <v-col>
                  <p>Foil Cards:</p>
                  <p>{{ current_set_owned_foils }}/{{ current_set_base_cards_qty + current_set_extra_cards_qty }}</p>
                </v-col>
              </v-row>
            </v-card>
            <v-progress-linear height="15" v-model="getProgressForSet"
              :color="getProgressForSet < 100 ? 'primary' : 'amber-lighten-2'">
              <template v-slot:default="{ value }">
                <strong>{{ Math.round(value * 10) / 10 }}%</strong>
              </template>
            </v-progress-linear>
          </v-card>
          <v-sheet name="normal_cards_holder">
            <v-row no-gutters>
              <v-col
                v-for="(item, index) in current_set_base_cards.filter((card) => (card.name.toLowerCase().includes(card_search.toLowerCase()) || card_search == '')).slice(pageSliceStart, pageSliceEnd)"
                cols="6" sm="6" md="4" lg="3">
                <CardSlot :card="item" :user_id="userId" :csrf_token="csrf_token" :collection_stock="collection_stock.o"
                  :current_set_code="current_set_code" :show_price="page_options.show_prices"
                  :dark_mode="page_options.dark_mode"
                  :is_extra="is_card_extra(item.promo_types)" :base_set_total="current_set_base_cards_qty"
                  :extra_set_total="current_set_extra_cards_qty" :current_set_commons="current_set_commons"
                  :current_set_uncommons="current_set_uncommons" :current_set_rares="current_set_rares"
                  :current_set_mythics="current_set_mythics"></CardSlot>
              </v-col>
            </v-row>
          </v-sheet>
        </v-sheet>
        <v-pagination v-if="page_options.card_per_page_option_selected.value !== 4" v-model="current_page"
          :length="pageCount"
          :total-visible="isMobile ? 4 : 8" />
        <v-card class="set_stats_box" :elevation="10" v-scroll="on_scroll_stats_box" v-show="stats_box_visible">
          <v-card class="set_stats_inner_box" flat>
            <p>Base Set: {{ current_set_owned_base_cards }}/{{ current_set_base_cards_qty }}</p>
            <p v-if="current_set_commons > 0">Commons: {{ current_set_owned_commons }}/{{ current_set_commons }}</p>
            <p v-if="current_set_uncommons > 0">Uncommons: {{ current_set_owned_uncommons }}/{{ current_set_uncommons }}
            </p>
            <p v-if="current_set_rares > 0">Rares: {{ current_set_owned_rares }}/{{ current_set_rares }}</p>
            <p v-if="current_set_mythics > 0">Mythic Rares: {{ current_set_owned_mythics }}/{{ current_set_mythics }}
            </p>
            <p v-if="current_set_extra_cards_qty > 0">Extra Cards: {{ current_set_owned_extra_cards }}/{{
              current_set_extra_cards_qty }}</p>
            <p>Grand Total: {{ current_set_owned_base_cards + current_set_owned_extra_cards }}/{{
              current_set_base_cards_qty +current_set_extra_cards_qty }}</p>
            <p>Foil Cards: {{ current_set_owned_foils }}/{{ current_set_base_cards_qty + current_set_extra_cards_qty }}
            </p>
          </v-card>
          <v-progress-linear height="15" v-model="getProgressForSet"
            :color="getProgressForSet < 100 ? 'primary' : 'amber-lighten-2'">
            <template v-slot:default="{ value }">
              <strong>{{ Math.round(value * 10) / 10 }}%</strong>
            </template>
          </v-progress-linear>
        </v-card>
      </v-main>
      <v-main class="intro_message_main" v-if="!isDecklistFinderPage && (!current_set || !current_set_base_cards)">
        <v-sheet class="intro_message_body rounded-lg" justify="center">
          <img class="title_logo" src="@/assets/collectron-title-logo.png" />
          <h2 class="intro_title">Welcome to the MTG Collectron</h2>
          <h3 class="intro_title">A visual collection tracker tool for Magic: the Gathering</h3>
          <br>
          <p>To get started, select a set name on the Set Navigation to the left, or open the Tools menu on the right.
          </p>
          <p>Hover/tap over cards to see the controls and add cards to your collection, or directly import them with the
            'Import Cards' tool.</p>
          <br>
          <v-divider />
          <br>
          <p style="padding:4px; font-size: 13px;">Magic: the Gathering, all card images, symbols and information
            associated
            with it, are copyrighted by Wizards of the Coast LLC, and I'm not affiliated with or endorsed by them.</p>
          <p style="padding:4px; font-size: 13px;">Card and set information, data searches, and visual information such
            as
            card and set icon pictures, are all sourced from Scryfall and its API. This site is not affiliated with them
            in
            any way, but I'm otherwise very grateful for their accessibility.</p>
          <br>
          <p style="padding:4px; font-size: 11px;">version 3.0.0 - last update 07/11/26</p>
        </v-sheet>
      </v-main>
      <v-card v-if="!isDecklistFinderPage">
        <v-navigation-drawer app temporary v-model="drawer" elevation="2" :width="isMobile ? '100%' : 300">
          <v-list>
            <v-list-item id="column_set_visib_title">
              <p class="column_header">Set Visibility</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="core" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <label for="check_core" style="display: inline-block;">Core Sets</label>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="expansion" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Expansions</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="masters" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Masters Sets</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="commander" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Commander Sets</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="draft_innovation" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Draft Innovation Sets</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="masterpiece" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Masterpieces</p>
            </v-list-item>
            <v-list-item>
              <input type="checkbox" value="all" v-model="set_types_shown"
                :class="page_options.dark_mode ? 'set_check_dark' : 'set_check'">
              <p style="display: inline-block;">Other Sets</p>
            </v-list-item>
          </v-list>
          <v-divider />
          <v-list-item>
            <p class="column_header">Search for Set</p>
          </v-list-item>
          <v-list-item><v-text-field v-model="set_search" prepend-inner-icon="mdi-magnify" variant="outlined"
              density="compact" /></v-list-item>
          <v-list-item>
            <p class="column_header">List of Sets</p>
          </v-list-item>
          <v-list-item v-for="set in set_list">
            <v-card @click="select_set(set)" class="set_list_element"
              :class="{ 'set_list_element_selected_light': set.code == current_set_code && !page_options.dark_mode, 'set_list_element_selected_dark': set.code == current_set_code && page_options.dark_mode, 'tertiary_hover_light': !page_options.dark_mode, 'tertiary_hover_dark': page_options.dark_mode }"
              variant="flat"
              v-show="set['digital'] == false && (set_types_shown.includes(set['set_type']) || (set_types_shown.includes('all') && !['core', 'expansion', 'commander', 'masters', 'draft_innovation', 'masterpiece'].includes(set['set_type']))) && (set_search == '' || set['name'].toLowerCase().includes(set_search.toLowerCase()) || set.code == set_search.toLowerCase()) && ((new Date(new Date().setDate(new Date().getDate() + 7))).toISOString().substring(0, 10) >= set.released_at) && set.card_count > 0">
              <v-img :src="set.icon_svg_uri" class="set_logo" :class="{ set_logo_white: page_options.dark_mode }"
                width="18px" height="18px" />
              <p class="set_list_name">{{ set.name }}</p>
            </v-card>
            <v-progress-linear rounded height="3" class="set_list_element_bar"
              :model-value="getProgressForSidebarSet(set.code)"
              :color="getProgressForSidebarSet(set.code) < 100 ? 'primary' : 'amber-lighten-2'"
              v-if="getProgressForSidebarSet(set.code) > 0 && page_options.show_sidebar_percent"
              v-show="set['digital'] == false && (set_types_shown.includes(set['set_type']) || (set_types_shown.includes('all') && !['core', 'expansion', 'commander', 'masters', 'draft_innovation', 'masterpiece'].includes(set['set_type']))) && (set_search == '' || set['name'].toLowerCase().includes(set_search.toLowerCase()) || set.code == set_search.toLowerCase()) && ((new Date(new Date().setDate(new Date().getDate() + 7))).toISOString().substring(0, 10) >= set.released_at)" />
          </v-list-item>
        </v-navigation-drawer>
      </v-card>
      <v-card>
        <v-navigation-drawer app temporary v-model="settings" elevation="2" location="right"
          :width="isMobile ? '100%' : 300">
          <v-list dense>
            <v-list-item>
              <p class="column_header">User Preferences</p>
            </v-list-item>
            <v-list-item style="display: inline-block; width:100%;">
              <v-switch v-model="page_options.dark_mode" label="Toggle Dark Mode" density="compact" hide-details="true"
                style="margin-left:10px;" color="primary" />
              <v-switch v-model="page_options.show_prices" label="Show Card Prices" density="compact"
                hide-details="true" style="margin-left:10px;" color="primary" />
              <v-switch v-model="page_options.show_sidebar_percent" label="Show % Bar on Setlist" density="compact"
                hide-details="true" style="margin-left:10px;" color="primary" />
              <v-select v-model="page_options.full_set_option_selected" label="Full Set Definition"
                :items="full_set_options" return-object>
                <v-tooltip activator="parent" location="bottom">Defines the objective considered for the progress bars
                  and
                  'full set' message displays for each set</v-tooltip>
              </v-select>
            </v-list-item>
            <v-divider />
            <v-list-item>
              <p class="column_header">Collection Functions</p>
            </v-list-item>
            <v-list-item style="display: inline-block; width:100%;">
              <v-btn @click="card_finder_window_active = true" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">Card Finder</v-btn>
              <v-btn v-if="!isDecklistFinderPage" @click="navigateToDecklistFinder" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">Decklist Finder</v-btn>
              <v-btn @click="import_window_active = true" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">Import Cards</v-btn>
              <v-btn @click="exportCollectionMenu" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">Export Collection</v-btn>
              <!--v-btn @click="housekeeping_window_active = true" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">Housekeeping Tasks</v-btn><!-->
            </v-list-item>
            <v-divider />
            <v-list-item>
              <p class="column_header">Information</p>
            </v-list-item>
            <v-list-item style="display: inline-block; width:100%;">
              <v-btn @click="about_window_active = true" class="side_drawer_button"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" density="comfortable"
                variant="outlined">About the Collectron</v-btn>
            </v-list-item>
            <v-divider />
            <v-list-item>
              <p class="column_header">Account</p>
            </v-list-item>
            <v-list-item style="display: inline-block; width:100%;">
              <p class="account_username">{{ authUser?.username || authUser?.email }}</p>
              <v-btn @click="logOut" class="side_drawer_button" density="comfortable" variant="outlined"
                :class="page_options.dark_mode ? 'tertiary_hover_dark' : 'tertiary_hover_light'" :loading="loggingOut">
                Log Out
              </v-btn>
            </v-list-item>
          </v-list>
        </v-navigation-drawer>
      </v-card>
    </v-app>
  </template>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch, reactive, computed, unref } from 'vue'
import { useTheme, useDisplay } from 'vuetify'
import CardSlot from './CardSlot.vue'
import DecklistFinder from './DecklistFinder.vue'
import FileSaver from 'file-saver'
import Login from './Login.vue'
import { AUTHENTICATION_REQUIRED_EVENT, authFetch } from './authFetch.js'

const isAuthenticated = ref(false)
const authChecking = ref(true)
const authError = ref('')
const authUser = ref(null)
const userId = ref(null)
const csrf_token = ref(null)
const loggingOut = ref(false)
const isDecklistFinderPage = ref(window.location.hash === '#decklist-finder')
let appInitialized = false
let appInitializationComplete = false

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
function toggleDarkMode(bool) {
  if (bool)
    theme.change('dark')
  else
    theme.change('light')
  // theme.global.name.value = bool ? 'dark' : 'light'
  // console.log(theme)
}


// ------------------------------------------------------------ //

var drawer = ref(true)          // signals the set navigation drawer is open
var settings = ref(false)       // signals the settings menu is open
var loading = ref(false)        // signals the loading circle is visible
var loading_bar = ref(false)    // signals the loading progress bar is visible
var loading_bar_fill = ref(0)  // fill value of the progress bar
var card_finder_window_active = ref(false)              // signals the card search dialog is visible
var import_window_active = ref(false)       // signals the import dialog is visible
var import_results_active = ref(false)      // signals the import dialog results are visible
var export_window_active = ref(false)       // signals the export dialog is visible
var housekeeping_window_active = ref(false) // signals the housekeeping window dialog is visible
var about_window_active = ref(false)        // signals the about window is visible

var card_finder_text = ref('')
var card_finder_results = ref([])
let cardFinderSearchTimeout
let cardFinderRequestController
let cardFinderSearchId = 0

var import_syntax = ref('moxfield')
var import_action = ref('add')
var import_replace_confirmed = ref(false)
var import_password = ref('')
var import_text = ''
var import_file_data = ref(null)
var import_success = ref(true)
var import_errors = ref([])
var import_card_total = ref(0)
var import_result_message = ref('')
var import_status_message = ref('')

var toast = ref(false)
var finished_housekeeping = ref(false)

const card_per_page_options = [
  { value: 1, title: 36 },
  { value: 2, title: 60 },
  { value: 3, title: 120 },
  //{value: 4, title: 'All'}
]
const full_set_options = [
  { value: 1, title: 'Every single card, variants included' },
  { value: 2, title: 'Base set only' },
  { value: 3, title: 'At least one version of each card name' }
]

var page_options = reactive({
  show_option_selected: 1,
  full_set_option_selected: full_set_options[0],
  card_per_page_option_selected: card_per_page_options[0],
  dark_mode: false,
  show_prices: true,
  show_sidebar_percent: true,
})

var set_list = ref([])
var set_types_shown = ref(['core', 'expansion'])
var set_search = ref('')
var card_search = ref('')

var collection_stock = reactive({ o: {} })  // the user's total card stock, a json object that includes every single card they own (oof?)
// the .o initial object is required to maintain reactivity, because if we overwrite the parent object, we lose reactive()

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
  { value: 1, title: 'All cards' },
  { value: 2, title: 'Only owned' },
  { value: 3, title: 'Only unowned' }
]

// -------------------------------------------------------------------------------------------------- //

function handleAuthenticationRequired() {
  if (!isAuthenticated.value) return

  authError.value = 'Your session has expired. Please log in again.'
  isAuthenticated.value = false
  authUser.value = null
  userId.value = null
  csrf_token.value = null
  loading.value = false
  loading_bar.value = false
  appInitialized = false
  appInitializationComplete = false
  current_set.value = null
}

function updatePageFromLocation() {
  isDecklistFinderPage.value = window.location.hash === '#decklist-finder'
  if (isDecklistFinderPage.value) {
    settings.value = false
  }
}

function navigateToDecklistFinder() {
  if (isDecklistFinderPage.value) return
  window.history.pushState({}, '', `${window.location.pathname}${window.location.search}#decklist-finder`)
  isDecklistFinderPage.value = true
  settings.value = false
}

function navigateToMainPage() {
  window.history.replaceState({}, '', `${window.location.pathname}${window.location.search}`)
  isDecklistFinderPage.value = false
}

onMounted(async () => {
  window.addEventListener(AUTHENTICATION_REQUIRED_EVENT, handleAuthenticationRequired)
  window.addEventListener('popstate', updatePageFromLocation)
  window.addEventListener('hashchange', updatePageFromLocation)

  try {
    const response = await authFetch('/mtg-collectron/auth/session', { credentials: 'include' })

    // A 401 is the normal unauthenticated state; every other non-success status indicates a
    // backend/configuration problem and is shown on the login screen instead of being ignored.
    if (response.status === 401) return
    if (!response.ok) throw new Error(`Unable to verify session (HTTP ${response.status}). Backend is likely not running.`)

    const session = await response.json()
    authUser.value = session.user ?? session
    userId.value = session.userId ?? getUserId(authUser.value)
    if (userId.value == null) {
      throw new Error('The authenticated session did not include a user ID.')
    }
    // console.log("userId.value",userId.value)
    isAuthenticated.value = true

    // CSRF token is necessary to validade most auth methods
    const csrfCall = await authFetch('/mtg-collectron/auth/csrf', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!csrfCall.ok) {
      throw new Error(`Unable to retrieve a CSRF token (HTTP ${csrfCall.status}).`)
    }
    const csrfCallResponse = await csrfCall.json()
    csrf_token.value = csrfCallResponse.token

    await initializeApp()
  } catch (error) {
    if (isAuthenticated.value || !authError.value) {
      authError.value = error instanceof Error
        ? error.message
        : 'Unable to verify your session. Please try again.'
    }
  } finally {
    authChecking.value = false
  }
})

onBeforeUnmount(() => {
  clearTimeout(cardFinderSearchTimeout)
  cardFinderSearchId++
  cardFinderRequestController?.abort()
  window.removeEventListener(AUTHENTICATION_REQUIRED_EVENT, handleAuthenticationRequired)
  window.removeEventListener('popstate', updatePageFromLocation)
  window.removeEventListener('hashchange', updatePageFromLocation)
})

async function initializeApp() {
  if (appInitialized) return
  appInitialized = true
  appInitializationComplete = false
  loading.value = true

  try {
    // Start with the set navigation closed on mobile.
    if (unref(display.mobile)) {
      drawer.value = false
    }

    // Restore display preferences after the user has been authenticated.
    const set_options = JSON.parse(localStorage.getItem('set_options'))
    if (set_options) { set_types_shown.value = set_options }
    await get_preferences_from_storage()

    // get all set data from the server, and directly afterwards, get the users' set info data as well
    set_list.value = await get_all_set_info()
    await refreshCollectionStockFromServer()
    // console.log("Collection stock: ", collection_stock.o)

  } catch (error) {
    if (isAuthenticated.value || !authError.value) {
      authError.value = error instanceof Error
        ? error.message
        : 'Unable to load your collection. Please try again.'
    }
  } finally {
    loading.value = false
    appInitializationComplete = true
  }
}

async function handleAuthenticated(user) {
  const authenticatedUserId = getUserId(user)
  if (authenticatedUserId == null) {
    authError.value = 'The authentication response did not include a user ID.'
    return
  }

  authUser.value = user
  userId.value = authenticatedUserId
  authError.value = ''
  isAuthenticated.value = true

  try {
    // CSRF token is necessary to validade most auth methods
    if (!csrf_token.value) {
      const csrfCall = await authFetch('/mtg-collectron/auth/csrf', {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!csrfCall.ok) {
        throw new Error(`Unable to retrieve a CSRF token (HTTP ${csrfCall.status}).`)
      }
      const csrfCallResponse = await csrfCall.json()
      csrf_token.value = csrfCallResponse.token
    }

    await initializeApp()
  } catch (error) {
    if (isAuthenticated.value) {
      authError.value = error instanceof Error
        ? error.message
        : 'Unable to complete authentication. Please try again.'
      isAuthenticated.value = false
      authUser.value = null
      userId.value = null
      csrf_token.value = null
      appInitialized = false
      appInitializationComplete = false
    }
  }
}

function getUserId(user) {
  return user?.id ?? user?.userId ?? user?.user_id
}

async function logOut() {
  loggingOut.value = true
  authError.value = ''
  current_set.value = null

  try {
    // CSRF token is necessary to validade most auth methods
    const csrfCall = await authFetch('/mtg-collectron/auth/csrf', {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    })
    if (!csrfCall.ok) {
      throw new Error(`Unable to retrieve a CSRF token (HTTP ${csrfCall.status}).`)
    }
    const csrfCallResponse = await csrfCall.json()

    // call logout, passing the CSRF token as a header to authenticate the message
    const response = await authFetch('/mtg-collectron/auth/logout', {
      method: 'POST',
      headers: { 'X-CSRF-Token': csrfCallResponse['token'] },
      credentials: 'include',
    })

    if (!response.ok) {
      throw new Error(`Unable to log out (HTTP ${response.status}).`)
    }

    isAuthenticated.value = false
    authUser.value = null
    userId.value = null
    appInitialized = false
    appInitializationComplete = false
  } catch (error) {
    authError.value = error instanceof Error ? error.message : 'Unable to log out. Please try again.'
  } finally {
    loggingOut.value = false
  }
}

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

  localStorage.setItem('collection_stock', JSON.stringify(new_obj.o))
})
// whenever the set options checklist changes, we save it
watch(set_types_shown, new_array => {
  localStorage.setItem('set_options', JSON.stringify(new_array))
})
watch(page_options, async () => {
  if (!appInitializationComplete) return

  toggleDarkMode(page_options.dark_mode)
  current_page.value = 1

  console.log("page_options being persisted: ",page_options)

  try {
    const response = await authFetch(
      `/mtg-collectron/user-preferences/${encodeURIComponent(userId.value)}`,
      {
        method: 'PATCH',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrf_token.value,
        },
        body: JSON.stringify({
          ...page_options,
          full_set_option_selected: page_options.full_set_option_selected.value,
          card_per_page_option_selected: page_options.card_per_page_option_selected.value,
        }),
      },
    )
    if (!response.ok) {
      throw new Error(`Unable to update user preferences (HTTP ${response.status}).`)
    }
  } catch (error) {
    authError.value = error instanceof Error
      ? error.message
      : 'Unable to update user preferences. Please try again.'
  }
})
watch(card_search, v => {
  current_page.value = 1
})
watch(card_finder_text, cardName => {
  clearTimeout(cardFinderSearchTimeout)
  cardFinderRequestController?.abort()
  cardFinderRequestController = undefined
  const searchId = ++cardFinderSearchId
  card_finder_results.value = []

  if (cardName.trim().length < 3 || userId.value == null) return

  cardFinderSearchTimeout = setTimeout(() => {
    findCardsInCollection(cardName.trim(), searchId)
  }, 300)
})
watch(current_page, v => {
  // scroll back to top on changing data pages
  window.scrollTo({ top: 0, behavior: "smooth" })
})

// on a page refresh, pulls all set data for the logged user from the server to populate the local cache
async function refreshCollectionStockFromServer() {
  const response = await authFetch(`/mtg-collectron/user-set-info/${encodeURIComponent(userId.value)}`, {
    method: 'GET',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
  })
  if (!response.ok) {
    throw new Error(`Unable to refresh collection set info (HTTP ${response.status}).`)
  }

  const setRows = await response.json()
  if (!Array.isArray(setRows)) {
    throw new Error('The collection set-info endpoint did not return a list.')
  }

  const freshStock = {}
  for (const row of setRows) {
    if (!row || typeof row.set_code !== 'string' || !row.set_code) {
      throw new Error('The collection set-info response contains a row without a set code.')
    }

    freshStock[row.set_code] = {
      cards: {},
      commons: row.commons_count ?? 0,
      uncommons: row.uncommons_count ?? 0,
      rares: row.rares_count ?? 0,
      mythics: row.mythics_count ?? 0,
      total_commons: 0,
      total_uncommons: 0,
      total_rares: 0,
      total_mythics: 0,
      base_set_owned: row.base_set_owned ?? 0,
      extra_owned: row.extra_set_owned ?? 0,
      foils_owned: row.foils_owned ?? 0,
      base_set_total: 0,
      extra_set_total: 0,
      full_set_every_single: row.full_set_every_single ?? 0,
      full_set_base_only: row.full_set_base_only ?? 0,
      full_set_one_each: row.full_set_one_each ?? 0,
    }
  }

  collection_stock.o = freshStock
}

// returns all cards for the current user of the selected set
async function getAllOwnedCardsForUserInSet(setCode) {
  var setStock = collection_stock.o[setCode]
  if (!setStock) {
    collection_stock.o[setCode] = {
      cards: {},
      commons: 0,
      uncommons: 0,
      rares: 0,
      mythics: 0,
      total_commons: 0,
      total_uncommons: 0,
      total_rares: 0,
      total_mythics: 0,
      base_set_owned: 0,
      extra_owned: 0,
      foils_owned: 0,
      base_set_total: 0,
      extra_set_total: 0,
      full_set_every_single: 0,
      full_set_base_only: 0,
      full_set_one_each: 0,
    }

    setStock = collection_stock.o[setCode]
  }

  const response = await authFetch(
    `/mtg-collectron/owncard/${encodeURIComponent(userId.value)}/${encodeURIComponent(setCode)}`,
    {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    },
  )
  if (!response.ok) {
    throw new Error(`Unable to load owned cards for set "${setCode}" (HTTP ${response.status}).`)
  }

  const ownedCards = await response.json()
  if (!Array.isArray(ownedCards)) {
    throw new Error(`The owned-card endpoint for set "${setCode}" did not return a list.`)
  }

  const cards = {}
  for (const ownedCard of ownedCards) {
    if (
      !ownedCard ||
      typeof ownedCard.card_name !== 'string' ||
      typeof ownedCard.collector_number !== 'string' ||
      ownedCard.set_code !== setCode
    ) {
      throw new Error(`The owned-card response for set "${setCode}" contains an invalid card.`)
    }

    const cardData = current_set_base_cards.value?.find(card =>
      card.name === ownedCard.card_name && card.collector_number === ownedCard.collector_number,
    )
    if (!cards[ownedCard.card_name]) {
      cards[ownedCard.card_name] = {}
    }
    cards[ownedCard.card_name][ownedCard.collector_number] = {
      count: ownedCard.card_count,
      foil: ownedCard.is_foil,
      extra: ownedCard.is_considered_extra,
      tag_square: ownedCard.is_tagged_square,
      tag_circle: ownedCard.is_tagged_circle,
      tag_triangle: ownedCard.is_tagged_triangle,
      tag_cross: ownedCard.is_tagged_cross,
      image: cardData ? getCardImage(cardData.image_uris, cardData.card_faces) : undefined,
    }
  }

  setStock.cards = cards
}

// activated when a set is selected on the left column, or a card is selected on Card Finder
// clean up previous values, set up the loading overlay, and grab the new data from the next set
async function select_set(set) {
  // console.log("collection stock for selected set",collection_stock.o[set.code])
  loading.value = true

  // if we already have a current set selected, and the set exists in the stock, we clear it up
  if (current_set.value) {
    const previousSetStock = collection_stock.o[current_set.value.code]
    if (previousSetStock) {
      previousSetStock.cards = {}
    }
  }

  current_page.value = 1
  card_search.value = ''
  current_set.value = set
  current_set_code.value = set.code

  // clean up previous set variables
  current_set_base_cards_qty.value = 0
  current_set_extra_cards_qty.value = 0
  current_set_commons.value = 0
  current_set_uncommons.value = 0
  current_set_rares.value = 0
  current_set_mythics.value = 0

  // grab a list of all cards 
  current_set_base_cards.value = await get_set_all_cards(set.code)

  // populate the selected set's card data from the server
  try {
    await getAllOwnedCardsForUserInSet(set.code)
  } catch (error) {
    loading.value = false
    throw error
  }

  var cards_checked = [] // list of cards already checked for rarity
  // we will go card by card to get the number that we consider 'base' and 'extra'
  for (var card in current_set_base_cards.value) {
    // seems like every card that I consider 'extra' has SOMETHING in promo_types (like boosterfun or bundle), so this neatly filters those out!
    // exception: FIN set has the original game (e.g. 'ffix') as the promo type for every card... goddamnit.
    if (is_card_extra(current_set_base_cards.value[card].promo_types)) {
      current_set_extra_cards_qty.value++
    } else {
      current_set_base_cards_qty.value++
    }

    // for "token" sets, since we can have multiple identically named tokens that are actually different tokens/creatures
    // we will append the card number to the token name to differentiate
    if (set.set_type == 'token') {
      current_set_base_cards.value[card].name += " " + current_set_base_cards.value[card].collector_number
    }

    // tally the rarities in the set; we only count each cardname once
    if (!cards_checked.includes(current_set_base_cards.value[card].name)) {
      cards_checked.push(current_set_base_cards.value[card].name)
      switch (current_set_base_cards.value[card].rarity) {
        case 'common':
          current_set_commons.value++
          break
        case 'uncommon':
          current_set_uncommons.value++
          break
        case 'rare':
          current_set_rares.value++
          break
        case 'mythic':
          current_set_mythics.value++
          break
        default:
          break
      }
    }
  }

  // if the set is already in our collection
  if (collection_stock.o[set.code]) {
    collection_stock.o[set.code].total_commons = current_set_commons.value
    collection_stock.o[set.code].total_uncommons = current_set_uncommons.value
    collection_stock.o[set.code].total_rares = current_set_rares.value
    collection_stock.o[set.code].total_mythics = current_set_mythics.value
    collection_stock.o[set.code].base_set_total = current_set_base_cards_qty.value
    collection_stock.o[set.code].extra_set_total = current_set_extra_cards_qty.value
  }

  current_set_owned_base_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].base_set_owned : 0
  current_set_owned_commons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].commons : 0
  current_set_owned_uncommons.value = collection_stock.o[set.code] ? collection_stock.o[set.code].uncommons : 0
  current_set_owned_rares.value = collection_stock.o[set.code] ? collection_stock.o[set.code].rares : 0
  current_set_owned_mythics.value = collection_stock.o[set.code] ? collection_stock.o[set.code].mythics : 0
  current_set_owned_extra_cards.value = collection_stock.o[set.code] ? collection_stock.o[set.code].extra_owned : 0
  current_set_owned_foils.value = collection_stock.o[set.code] ? collection_stock.o[set.code].foils_owned : 0

  // console.log("current set data:",current_set_base_cards.value)

  // close the set navigation tab after selecting the set, if on mobile
  if (unref(display.mobile)) {
    drawer.value = false
  }
  loading.value = false
}

// recovers the user preferences from the database and sets up the screen based on them
async function get_preferences_from_storage() {
  const response = await authFetch(
    `/mtg-collectron/user-preferences/${encodeURIComponent(userId.value)}`,
    {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    },
  )
  if (!response.ok) {
    throw new Error(`Unable to load user preferences (HTTP ${response.status}).`)
  }

  const stored_options = await response.json()
  if (stored_options !== null) {
    const optionNames = [
      'full_set_option_selected',
      'card_per_page_option_selected',
      'dark_mode',
      'show_prices',
      'show_sidebar_percent',
    ]
    if (
      typeof stored_options !== 'object' ||
      Array.isArray(stored_options) ||
      optionNames.some(optionName => !Object.prototype.hasOwnProperty.call(stored_options, optionName))
    ) {
      throw new Error('The user-preferences endpoint returned invalid preferences.')
    }

    const storedFullSetOption = full_set_options.find(
      option => option.value === stored_options.full_set_option_selected,
    )
    if (!storedFullSetOption) {
      throw new Error('The user-preferences endpoint returned an invalid full-set option.')
    }
    const storedCardsPerPageOption = card_per_page_options.find(
      option => option.value === stored_options.card_per_page_option_selected,
    )
    if (!storedCardsPerPageOption) {
      throw new Error('The user-preferences endpoint returned an invalid cards-per-page option.')
    }
    page_options.full_set_option_selected = storedFullSetOption
    page_options.card_per_page_option_selected = storedCardsPerPageOption
    page_options.dark_mode = stored_options.dark_mode
    page_options.show_prices = stored_options.show_prices
    page_options.show_sidebar_percent = stored_options.show_sidebar_percent
  } else {
    const user_options = {
      full_set_option_selected: full_set_options[0],
      card_per_page_option_selected: card_per_page_options[1],
    }
    page_options.full_set_option_selected = user_options.full_set_option_selected
    page_options.card_per_page_option_selected = user_options.card_per_page_option_selected
    page_options.dark_mode = false
    page_options.show_prices = true
    page_options.show_sidebar_percent = true
  }
  // after options are populated, we change to dark mode (or not)
  toggleDarkMode(page_options.dark_mode)
}

// get all set information from the db
async function get_all_set_info() {
  var fetch_url = "/mtg-collectron/sets"

  // since the migration to a spring boot backend, we query our data directly from our db
  const response = await authFetch(fetch_url);
  return await response.json();
}

// get all card information for the selected set
async function get_set_all_cards(set_code) {
  var fetch_url = "/mtg-collectron/card/" + (set_code.toLowerCase())

  // since the migration to a spring boot backend, we query our data directly from our db
  const response = await authFetch(fetch_url);
  return await response.json();
}

// Returns owned printings that partially match the typed card name.
async function findCardsInCollection(cardName, searchId) {
  const controller = new AbortController()
  cardFinderRequestController = controller

  try {
    const response = await authFetch(
      '/mtg-collectron/owncard/card-finder',
      {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrf_token.value,
        },
        body: JSON.stringify({
          card_owner_id: userId.value,
          card_name: cardName,
        }),
        signal: controller.signal,
      },
    )
    if (!response.ok) {
      throw new Error(`Unable to search your collection (HTTP ${response.status}).`)
    }

    const ownedCards = await response.json()
    if (!Array.isArray(ownedCards)) {
      throw new Error('The card-finder endpoint did not return a list.')
    }

    const cardList = ownedCards.map(card => {
      if (
        !card ||
        typeof card.card_name !== 'string' ||
        typeof card.set_code !== 'string' ||
        typeof card.collector_number !== 'string'
      ) {
        throw new Error('The card-finder response contains an invalid card.')
      }

      const tagSquare = card.is_tagged_square ? '■' : ''
      const tagTriangle = card.is_tagged_triangle ? '▲' : ''
      const tagCircle = card.is_tagged_circle ? '⚫︎' : ''
      const tagCross = card.is_tagged_cross ? '✖' : ''
      const formattedCardName =
        `${card.card_name} (${card.set_code.toUpperCase()}-${card.collector_number}) ` +
        `${tagSquare}${tagTriangle}${tagCircle}${tagCross}`

      return {
        cardName: card.card_name,
        cardSet: card.set_code,
        formattedCardName,
      }
    })
    cardList.sort(compareCards)

    if (searchId === cardFinderSearchId) {
      card_finder_results.value = cardList
    }
  } catch (error) {
    if (error?.name !== 'AbortError' && searchId === cardFinderSearchId) {
      authError.value = error instanceof Error
        ? error.message
        : 'Unable to search your collection. Please try again.'
    }
  } finally {
    if (cardFinderRequestController === controller) {
      cardFinderRequestController = undefined
    }
  }
}

// upon selecting a card on the card finder, go to the set selected and search for the typed card
async function goToFoundCard(cardName, cardSet) {
  try {
    const set = set_list.value.find(e => e.code.toLowerCase() == cardSet.toLowerCase())
    await select_set(set)
    card_finder_window_active.value = false
    card_finder_text.value = ''
    card_finder_results.value = []
    card_search.value = cardName
    if (isMobile) {   // on mobile we hide the settings window again to get it out of the way
      settings.value = false
    }
  }
  catch (err) {
    console.log("An error has occurred on goToFoundCard:", err)
  }
}

// parse and import list of cards on the text box
async function import_cards() {
  import_success.value = false
  import_errors.value = ''
  import_result_message.value = ''
  import_card_total.value = 0
  import_status_message.value = ''
  loading.value = true
  import_results_active.value = false

  try {
    if (import_syntax.value == 'moxfield') {
      await import_from_moxfield()
    }
    else if (import_syntax.value == 'native') {
      await import_from_native()
    }
  } catch (error) {
    import_success.value = false
    import_errors.value = error instanceof Error ? error.message : 'Unable to import the collection.'
  } finally {
    loading.value = false
    import_status_message.value = ''
    import_results_active.value = true
  }
}

// imports cards with the moxfield syntax
async function import_from_moxfield() {
  let cards_imported = 0
  // first, we split the list of cards imported, one per line
  var split_cards = import_text.split('\n')
  import_text = ''

  var error_list = []
  // then, we iterate through the list
  for (let i = 0; i < split_cards.length; i++) {
    try {
      // for each card, we set up a return object to later use to push the card
      var card = { 'name': '', 'amount': 0, 'set': '', 'collector_number': 0, 'foil': false, 'extra': false }

      // first we split the card by ' (' (note the space), the first half is the quantity and card name, the second half is the set name, collector number and modifiers
      const card_elements = split_cards[i].split(' (')
      // then we split the first part in two at the first space, and grab the first element as the amount
      const amount = card_elements[0].split(' ', 1)[0]
      // if the first element is not a number, it's an error
      if (parseInt(amount)) {
        card.amount = amount
      } else {
        throw EvalError()
      }
      // the remaining elements of the first part should be the card name
      card.name = card_elements[0].substring(card_elements[0].indexOf(' ') + 1)
      // console.log('card.name',card.name)

      // the second part, past the first parentheses, is further split by the second parentheses; the first element is the set, the second (if exists) may indicate foil
      const second_part = card_elements[1].split(') ')
      const third_part = second_part[1]?.split(' ')
      card.set = second_part[0].toLowerCase()
      card.collector_number = third_part[0]
      
      if (third_part.length >= 2 && ['*F*', '*E*'].includes(third_part[1])) {
        card.foil = true
      }

      await add_card_to_stock(card)
      cards_imported++
    }
    catch (e) {
      console.log("Error: ", e)
      error_list.push(split_cards[i])
    }
  }
  // we consider the import a success if at least one card was imported
  import_success.value = (cards_imported > 0)
  import_card_total.value = cards_imported
  import_errors.value = error_list.join(', ')
}

function loadImportFileToMemory(event) {
  import_file_data.value = event?.target?.files?.[0] ?? null
}

async function getImportResponseError(response, fallbackMessage) {
  const responseBody = await response.text()
  if (!responseBody) {
    return `${fallbackMessage} (HTTP ${response.status}).`
  }

  try {
    const errorResponse = JSON.parse(responseBody)
    return errorResponse.message || errorResponse.error || responseBody
  } catch {
    return responseBody
  }
}

async function readImportJobResponse(response) {
  if (!response.ok) {
    throw new Error(await getImportResponseError(response, 'Unable to retrieve the CSV import job.'))
  }

  try {
    const job = await response.json()
    if (!job || typeof job !== 'object' || Array.isArray(job)) {
      throw new Error('The import server returned an invalid job response.')
    }
    return job
  } catch {
    throw new Error('The import server returned an invalid job response.')
  }
}

async function waitForImportJob(jobId) {
  let job
  while (!job || job.state === 'queued' || job.state === 'running') {
    const response = await authFetch(
      `/mtg-collectron/importbackup/jobs/${encodeURIComponent(jobId)}`,
      { credentials: 'include' },
    )
    job = await readImportJobResponse(response)

    if (job.state === 'failed') {
      throw new Error(job.error || 'The CSV import failed.')
    }
    if (job.state !== 'queued' && job.state !== 'running' && job.state !== 'completed') {
      throw new Error('The import server returned an unknown job state.')
    }

    if (job.state !== 'completed') {
      import_status_message.value = job.state === 'queued'
        ? 'CSV import queued. Waiting for the import worker...'
        : "CSV import is running. This may take several minutes...\nPlease don't close this screen or use the site in other tabs to avoid data loss."
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
  }
  return job
}

// imports a CSV backup through the authenticated backup endpoint
async function import_from_native() {
  const file = import_file_data.value
  if (!file) {
    throw new Error('Select a CSV file to import.')
  }
  if (!/\.csv$/i.test(file.name) || (file.type && ![
    'text/csv',
    'application/csv',
    'application/vnd.ms-excel',
    'text/plain',
    'application/octet-stream',
  ].includes(file.type))) {
    throw new Error('The selected file must be a CSV file.')
  }
  if (userId.value == null) {
    throw new Error('User ID is not retrievable for some reason. A normal user should not be seeing this, contact me!')
  }
  if (!import_password.value.trim()) {
    throw new Error('Enter your password to import the collection.')
  }
  if (import_action.value == 'replace' && !import_replace_confirmed.value) {
    throw new Error('Confirm the collection replacement before importing. This message should not be reachable.')
  }
  if (!csrf_token.value) {
    throw new Error('The security token is unavailable. Refresh the page and try again.')
  }

  const formData = new FormData()
  formData.append('userId', String(userId.value))
  formData.append('password', import_password.value)
  formData.append('file', file, file.name)
  formData.append('additiveImport', String(import_action.value == 'add'))

  import_status_message.value = 'Uploading CSV and starting the import...'
  try {
    const response = await authFetch('/mtg-collectron/importbackup', {
      method: 'POST',
      credentials: 'include',
      headers: { 'X-CSRF-Token': csrf_token.value },
      body: formData,
    })
    if (!response.ok) {
      throw new Error(await getImportResponseError(response, 'Backup import failed'))
    }

    const acceptedJob = await readImportJobResponse(response)
    if (typeof acceptedJob.jobId !== 'string' || !acceptedJob.jobId) {
      throw new Error('The import server did not return a job ID.')
    }
    import_status_message.value = 'CSV import queued. Waiting for the import worker...'

    const completedJob = await waitForImportJob(acceptedJob.jobId)
    import_success.value = true
    import_card_total.value = completedJob.cardsImported ?? 0
    const importActionMessage = import_action.value == 'add'
      ? 'cards were added to your collection.'
      : 'your collection was replaced.'
    const setSummary = Number.isInteger(completedJob.setsImported)
      ? ` (${completedJob.setsImported} sets)`
      : ''
    import_result_message.value = `CSV import completed${setSummary}; ${importActionMessage}`

    try {
      await refreshCollectionStockFromServer()
      if (current_set.value) {
        if (collection_stock.o[current_set.value.code]) {
          await getAllOwnedCardsForUserInSet(current_set.value.code)
        } else {
          current_set_owned_base_cards.value = 0
          current_set_owned_commons.value = 0
          current_set_owned_uncommons.value = 0
          current_set_owned_rares.value = 0
          current_set_owned_mythics.value = 0
          current_set_owned_extra_cards.value = 0
          current_set_owned_foils.value = 0
        }
      }
    } catch (error) {
      const refreshError = error instanceof Error ? error.message : 'Unknown refresh error.'
      import_result_message.value += ` The import succeeded, but the collection view could not be refreshed: ${refreshError}`
    }
  } finally {
    import_password.value = ''
  }
}

function exportCollectionMenu() {
  export_window_active.value = true
}

async function saveCollectionFile() {
  try {
    if (userId.value == null) {
      throw new Error('Unable to export collection data without a user ID.')
    }

    const requestOptions = {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    }
    const [cardsResponse, setsResponse] = await Promise.all([
      authFetch(`/mtg-collectron/owncard/${encodeURIComponent(userId.value)}`, requestOptions),
      authFetch(`/mtg-collectron/user-set-info/${encodeURIComponent(userId.value)}`, requestOptions),
    ])
    if (!cardsResponse.ok) {
      throw new Error(`Unable to export card information (HTTP ${cardsResponse.status}).`)
    }
    if (!setsResponse.ok) {
      throw new Error(`Unable to export set information (HTTP ${setsResponse.status}).`)
    }

    const [cardRows, setRows] = await Promise.all([
      cardsResponse.json(),
      setsResponse.json(),
    ])
    if (!Array.isArray(cardRows) || !Array.isArray(setRows)) {
      throw new Error('The collection export endpoints did not return lists.')
    }

    const csvEscape = value => {
      const text = value == null
        ? ''
        : typeof value === 'object'
          ? JSON.stringify(value)
          : String(value)
      return `"${text.replaceAll('"', '""')}"`
    }
    const csvSection = (sectionName, rows, leadingColumns) => {
      if (rows.some(row => row === null || typeof row !== 'object' || Array.isArray(row))) {
        throw new Error(`The ${sectionName} export contains an invalid row.`)
      }

      const allColumns = [...new Set(rows.flatMap(row => Object.keys(row)))]
        .filter(column => column !== 'card_owner_id')
      const columns = [
        ...leadingColumns.filter(column => allColumns.includes(column)),
        ...allColumns.filter(column => !leadingColumns.includes(column)),
      ]
      return [
        csvEscape(sectionName),
        columns.map(csvEscape).join(','),
        ...rows.map(row => columns.map(column => csvEscape(row[column])).join(',')),
      ].join('\r\n')
    }
    const csv = [
      csvSection('card_info', cardRows, ['card_name', 'set_code']),
      csvSection('set_info', setRows, ['set_code']),
    ].join('\r\n\r\n')

    const d = new Date()
    const formatted_date = d.getFullYear() + "_" + (d.getMonth() + 1).toString().padStart(2, "0") + "_" + d.getDate().toString().padStart(2, "0")
    FileSaver.saveAs(
      new Blob(["\uFEFF", csv], { type: 'text/csv;charset=utf-8' }),
      `mtg_collectron_export_${formatted_date}.csv`,
    )
    authError.value = ''
  } catch (error) {
    authError.value = error instanceof Error
      ? error.message
      : 'Unable to export collection data. Please try again.'
  }
}

// Adds imported cards and persists the owned-card and set summaries.
async function add_card_to_stock(card) {
  const ownerId = userId.value
  if (ownerId == null) {
    throw new Error('Unable to add a card without an authenticated user ID.')
  }
  if (!csrf_token.value) {
    throw new Error('The security token is unavailable. Refresh the page and try again.')
  }

  const setCode = String(card.set).toLowerCase()
  const collectorNumber = String(card.collector_number)
  const amount = Number(card.amount)
  if (!Number.isSafeInteger(amount) || amount <= 0) {
    throw new Error(`Invalid card quantity for "${card.name}".`)
  }

  const cardResponse = await authFetch(
    `/mtg-collectron/card/bynumber/${encodeURIComponent(setCode)}/${encodeURIComponent(collectorNumber)}`,
    { credentials: 'include' },
  )
  if (!cardResponse.ok) {
    throw new Error(`Unable to load card ${collectorNumber} from set "${setCode}" (HTTP ${cardResponse.status}).`)
  }
  const cardResults = await cardResponse.json()
  const cardData = Array.isArray(cardResults) ? cardResults[0] : null
  if (!cardData) {
    throw new Error(`Card ${collectorNumber} was not found in set "${setCode}".`)
  }

  const setCards = current_set.value?.code === setCode && current_set_base_cards.value.length
    ? current_set_base_cards.value
    : await get_set_all_cards(setCode)
  if (!Array.isArray(setCards) || setCards.length === 0) {
    throw new Error(`Unable to load card data for set "${setCode}".`)
  }

  const ownedCardsResponse = await authFetch(
    `/mtg-collectron/owncard/${encodeURIComponent(ownerId)}/${encodeURIComponent(setCode)}`,
    {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    },
  )
  if (!ownedCardsResponse.ok) {
    throw new Error(`Unable to load owned cards for set "${setCode}" (HTTP ${ownedCardsResponse.status}).`)
  }
  const ownedCards = await ownedCardsResponse.json()
  if (!Array.isArray(ownedCards)) {
    throw new Error(`The owned-card endpoint for set "${setCode}" did not return a list.`)
  }
  for (const ownedCard of ownedCards) {
    if (
      !ownedCard ||
      typeof ownedCard.card_name !== 'string' ||
      typeof ownedCard.collector_number !== 'string' ||
      ownedCard.set_code !== setCode ||
      !Number.isSafeInteger(Number(ownedCard.card_count)) ||
      Number(ownedCard.card_count) < 0
    ) {
      throw new Error(`The owned-card response for set "${setCode}" contains an invalid card.`)
    }
  }

  const existingCard = ownedCards.find(ownedCard =>
    ownedCard?.set_code === setCode &&
    String(ownedCard.collector_number) === collectorNumber,
  )

  const isExtra = is_card_extra(cardData.promo_types)
  const isFoilOnly = (cardData.foil || cardData.finishes?.includes('etched')) && !cardData.nonfoil
  const isFoil = Boolean(card.foil || isFoilOnly)
  const setInfoResponse = await authFetch(
    `/mtg-collectron/user-set-info/${encodeURIComponent(ownerId)}/${encodeURIComponent(setCode)}`,
    {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
    },
  )
  if (setInfoResponse.status === 404) {
    const createSetResponse = await authFetch('/mtg-collectron/user-set-info/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrf_token.value,
      },
      body: JSON.stringify({
        card_owner_id: ownerId,
        set_code: setCode,
        commons_count: 0,
        uncommons_count: 0,
        rares_count: 0,
        mythics_count: 0,
        base_set_owned: 0,
        extra_set_owned: 0,
        foils_owned: 0,
        full_set_every_single: 0,
        full_set_base_only: 0,
        full_set_one_each: 0,
      }),
    })
    if (!createSetResponse.ok) {
      throw new Error(`Unable to create collection data for set "${setCode}" (HTTP ${createSetResponse.status}).`)
    }
  } else if (!setInfoResponse.ok) {
    throw new Error(`Unable to check collection data for set "${setCode}" (HTTP ${setInfoResponse.status}).`)
  }

  const cardWriteResponse = await authFetch('/mtg-collectron/owncard/', {
    method: existingCard ? 'PATCH' : 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrf_token.value,
    },
    body: JSON.stringify(existingCard
      ? {
          card_owner_id: ownerId,
          set_code: setCode,
          collector_number: collectorNumber,
          card_count: Number(existingCard.card_count) + amount,
          ...(isFoil && !existingCard.is_foil ? { is_foil: true } : {}),
        }
      : {
          card_owner_id: ownerId,
          set_code: setCode,
          card_name: cardData.name,
          collector_number: collectorNumber,
          card_count: amount,
          is_foil: isFoil,
          is_considered_extra: isExtra,
          is_tagged_square: false,
          is_tagged_circle: false,
          is_tagged_triangle: false,
          is_tagged_cross: false,
        }),
  })
  if (!cardWriteResponse.ok) {
    throw new Error(`Unable to ${existingCard ? 'update' : 'add'} card ${collectorNumber} (HTTP ${cardWriteResponse.status}).`)
  }

  const updatedOwnedCards = existingCard
    ? ownedCards.map(ownedCard => ownedCard === existingCard
        ? {
            ...ownedCard,
            card_count: Number(existingCard.card_count) + amount,
            is_foil: existingCard.is_foil || isFoil,
          }
        : ownedCard)
    : [
        ...ownedCards,
        {
          card_owner_id: ownerId,
          set_code: setCode,
          card_name: cardData.name,
          collector_number: collectorNumber,
          card_count: amount,
          is_foil: isFoil,
          is_considered_extra: isExtra,
          is_tagged_square: false,
          is_tagged_circle: false,
          is_tagged_triangle: false,
          is_tagged_cross: false,
        },
      ]

  const rarityTotals = { common: 0, uncommon: 0, rare: 0, mythic: 0 }
  const countedRarities = new Set()
  let totalBase = 0
  let totalExtra = 0
  for (const setCard of setCards) {
    if (is_card_extra(setCard.promo_types)) {
      totalExtra++
    } else {
      totalBase++
    }
    if (!countedRarities.has(setCard.name) && Object.prototype.hasOwnProperty.call(rarityTotals, setCard.rarity)) {
      countedRarities.add(setCard.name)
      rarityTotals[setCard.rarity]++
    }
  }

  const ownedRarities = { common: 0, uncommon: 0, rare: 0, mythic: 0 }
  const countedOwnedRarities = new Set()
  const ownedCardsByName = {}
  let baseSetOwned = 0
  let extraOwned = 0
  let foilsOwned = 0
  for (const ownedCard of updatedOwnedCards) {
    const setCard = setCards.find(candidate =>
      candidate.name === ownedCard.card_name &&
      String(candidate.collector_number) === ownedCard.collector_number,
    )
    if (!ownedCardsByName[ownedCard.card_name]) {
      ownedCardsByName[ownedCard.card_name] = {}
    }
    ownedCardsByName[ownedCard.card_name][ownedCard.collector_number] = {
      count: ownedCard.card_count,
      foil: ownedCard.is_foil,
      extra: ownedCard.is_considered_extra,
      tag_square: ownedCard.is_tagged_square,
      tag_circle: ownedCard.is_tagged_circle,
      tag_triangle: ownedCard.is_tagged_triangle,
      tag_cross: ownedCard.is_tagged_cross,
      image: setCard ? getCardImage(setCard.image_uris, setCard.card_faces) : undefined,
    }

    if (ownedCard.is_considered_extra) {
      extraOwned++
    } else {
      baseSetOwned++
    }
    if (ownedCard.is_foil) {
      foilsOwned++
    }
    if (
      setCard &&
      !countedOwnedRarities.has(ownedCard.card_name) &&
      Object.prototype.hasOwnProperty.call(ownedRarities, setCard.rarity)
    ) {
      countedOwnedRarities.add(ownedCard.card_name)
      ownedRarities[setCard.rarity]++
    }
  }

  const totalSetCards = totalBase + totalExtra
  const totalRarityCards = Object.values(rarityTotals).reduce((total, count) => total + count, 0)
  const ownedRarityCards = Object.values(ownedRarities).reduce((total, count) => total + count, 0)
  const fullSetEverySingle = totalSetCards > 0
    ? ((baseSetOwned + extraOwned) / totalSetCards) * 100
    : 0
  const fullSetBaseOnly = totalBase > 0 ? (baseSetOwned / totalBase) * 100 : 0
  const fullSetOneEach = totalRarityCards > 0 ? (ownedRarityCards / totalRarityCards) * 100 : 0
  const updatedSet = {
    card_owner_id: ownerId,
    set_code: setCode,
    commons_count: ownedRarities.common,
    uncommons_count: ownedRarities.uncommon,
    rares_count: ownedRarities.rare,
    mythics_count: ownedRarities.mythic,
    base_set_owned: baseSetOwned,
    extra_set_owned: extraOwned,
    foils_owned: foilsOwned,
    full_set_every_single: fullSetEverySingle,
    full_set_base_only: fullSetBaseOnly,
    full_set_one_each: fullSetOneEach,
  }

  const updateSetResponse = await authFetch('/mtg-collectron/user-set-info/', {
    method: 'PATCH',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrf_token.value,
    },
    body: JSON.stringify(updatedSet),
  })
  if (!updateSetResponse.ok) {
    throw new Error(`Unable to update collection data for set "${setCode}" (HTTP ${updateSetResponse.status}).`)
  }

  collection_stock.o[setCode] = {
    ...(collection_stock.o[setCode] || {}),
    cards: ownedCardsByName,
    commons: ownedRarities.common,
    uncommons: ownedRarities.uncommon,
    rares: ownedRarities.rare,
    mythics: ownedRarities.mythic,
    total_commons: rarityTotals.common,
    total_uncommons: rarityTotals.uncommon,
    total_rares: rarityTotals.rare,
    total_mythics: rarityTotals.mythic,
    base_set_owned: baseSetOwned,
    extra_owned: extraOwned,
    foils_owned: foilsOwned,
    base_set_total: totalBase,
    extra_set_total: totalExtra,
    full_set_every_single: fullSetEverySingle,
    full_set_base_only: fullSetBaseOnly,
    full_set_one_each: fullSetOneEach,
    released_at: cardData.released_at,
  }
}

// passing the card images uri array and possible card faces object, return an image uri, prioritizing images uri, and trimmed accordingly
function getCardImage(uriArray, cardFacesArray) {
  if (uriArray) {
    return uriArray['normal'].replace("https://cards.scryfall.io/normal/front/", "")
  }
  else if (cardFacesArray) {
    return cardFacesArray[0]['image_uris']['normal'].replace("https://cards.scryfall.io/normal/front/", "")
  }
  else return
}

// goes through all of the sets in the user's collection, recalculates values and percentages, and backfills missing values
async function tidy_up_collection() {
  try {
    loading_bar.value = true
    loading_bar_fill.value = 0
    let sets_done = 0
    const total_sets_owned = Object.keys(collection_stock.o).length
    // for each set the user currently owns at least one card of, we will query for it and use that info to backfill
    for (var set in collection_stock.o) {
      sets_done++
      loading_bar_fill.value = (sets_done / total_sets_owned) * 100
      if (collection_stock.o[set].done_processing)
        continue  // allows us to start from halfway through in case the tidying up process is interrupted

      console.log("Tidying collection, set " + sets_done + " of " + total_sets_owned + ": " + set)

      // get all set's cards from scryfall (yes, ouch)
      let set_card_data = await get_set_all_cards(set)

      // fill release date
      collection_stock.o[set].released_at = set_card_data[0].released_at

      // we go through all of our owned cards in this set and count base, extra, and foils owned
      let current_commons = 0, current_uncommons = 0, current_rares = 0, current_mythics = 0,
        current_foils = 0, current_base = 0, current_extra = 0
      let total_base = 0, total_extra = 0, total_commons = 0, total_uncommons = 0,
        total_rares = 0, total_mythics = 0
      let cards_checked = []

      // for each card in the current set we're querying...
      set_card_data.forEach((card) => {
        let in_col = false

        // if the card has promo types, it's extra, else base (for counting set totals)
        if (!is_card_extra(card.promo_types)) {
          total_base++
        } else {
          total_extra++
        }

        // for "token" sets, since we can have multiple identically named tokens that are actually different tokens/creatures
        // we will append the card number to the token name to differentiate
        if (card.set_type == 'token') {
          card.name += " " + card.collector_number
        }

        // if the card name exists in our collection stock...
        if (collection_stock.o[set].cards[card.name]) {
          // tag it in_col, i.e. we have at least one of this card, for rarity purposes
          in_col = true
          // console.log(collection_stock.o[set].cards[card.name][card.collector_number])

          // if the print number of the specific card we are looking at exists in our collection under its name, we own it
          if (collection_stock.o[set].cards[card.name][card.collector_number]) {
            // save the image path
            collection_stock.o[set].cards[card.name][card.collector_number].image = getCardImage(card['image_uris'], card['card_faces'])
            // set base/extra depending on promo_types
            if (!is_card_extra(card.promo_types)) {
              current_base++
            } else {
              current_extra++
            }
            // set if it's foil
            if (collection_stock.o[set].cards[card.name][card.collector_number].foil) {
              current_foils++
            }
          }
        }
        // tally the rarities in the set; we only count each cardname once
        if (!cards_checked.includes(card.name)) {
          cards_checked.push(card.name)
          switch (card.rarity) {
            case 'common':
              total_commons++
              if (in_col) { current_commons++ }
              break
            case 'uncommon':
              total_uncommons++
              if (in_col) { current_uncommons++ }
              break
            case 'rare':
              total_rares++
              if (in_col) { current_rares++ }
              break
            case 'mythic':
              total_mythics++
              if (in_col) { current_mythics++ }
              break
            default:
              break
          }
        }
      })

      // finally, set all the values based on what was calculated
      collection_stock.o[set].commons = current_commons
      collection_stock.o[set].uncommons = current_uncommons
      collection_stock.o[set].rares = current_rares
      collection_stock.o[set].mythics = current_mythics
      collection_stock.o[set].total_commons = total_commons
      collection_stock.o[set].total_uncommons = total_uncommons
      collection_stock.o[set].total_rares = total_rares
      collection_stock.o[set].total_mythics = total_mythics
      collection_stock.o[set].base_set_owned = current_base
      collection_stock.o[set].extra_owned = current_extra
      collection_stock.o[set].foils_owned = current_foils
      collection_stock.o[set].base_set_total = total_base
      collection_stock.o[set].extra_set_total = total_extra

      calculate_completion_for_set(set)

      collection_stock.o[set].done_processing = true

      loading_bar_fill.value = (sets_done / total_sets_owned) * 100
    }

    // at the end, clean up the "done processing flags"
    for (var set in collection_stock.o) {
      delete collection_stock.o[set].done_processing
    }
    console.log("collection", collection_stock.o)
    // ---
  } catch (err) {
    console.log(err)
  } finally {
    loading_bar.value = false
    finished_housekeeping.value = true
  }
}

// recalculate the full set percentage counters for the passed set
function calculate_completion_for_set(set) {
  collection_stock.o[set].full_set_every_single = ((collection_stock.o[set].base_set_owned + collection_stock.o[set].extra_owned) / (collection_stock.o[set].base_set_total + collection_stock.o[set].extra_set_total)) * 100
  collection_stock.o[set].full_set_base_only = (collection_stock.o[set].base_set_owned / collection_stock.o[set].base_set_total) * 100
  const dividend = collection_stock.o[set].commons + collection_stock.o[set].uncommons + collection_stock.o[set].rares + collection_stock.o[set].mythics
  const divisor = (collection_stock.o[set].total_commons ? collection_stock.o[set].total_commons : 0) + (collection_stock.o[set].total_uncommons ? collection_stock.o[set].total_uncommons : 0) + (collection_stock.o[set].total_rares ? collection_stock.o[set].total_rares : 0) + (collection_stock.o[set].total_mythics ? collection_stock.o[set].total_mythics : 0)
  collection_stock.o[set].full_set_one_each = divisor > 0 ? (dividend / divisor) * 100 : 0
}

// checks whether a card is considered a base or extra, by analyzing its promo_types block
function is_card_extra(promo_types) {
  // if a card has no promo types, or only promo types from the ignored_types category, it's considered base
  const ignored_types = ['universesbeyond', 'ffi', 'ffii', 'ffiii', 'ffiv', 'ffv', 'ffvi', 'ffvii', 'ffviii', 'ffix', 'ffx', 'ffxi', 'ffxii', 'ffxiii', 'ffxiv', 'ffxv', 'ffxvi']
  if (!promo_types) return false
  else {
    for (var type in promo_types) {
      if (!ignored_types.includes(promo_types[type]))
        return true
    }
    return false
  }
}

// removes the collection stock entirely, deleting all data
function clear_all_data() {
  if (clicks_to_clear.value < 9) {
    clicks_to_clear.value++
  }
  else {
    clicks_to_clear.value = 0
    collection_stock.o = {}
    localStorage.removeItem('collection_stock')
    location.reload()
  }
}

// -------------------- COMPUTED BLOCK --------------------------- //

const getProgressForSet = computed(() => {
  if (collection_stock.o[current_set_code.value]) {
    const setStock = collection_stock.o[current_set_code.value]
    switch (page_options.full_set_option_selected.value) {
      case 1: // every single card, variants included
        return setStock.full_set_every_single || (setStock.base_set_total + setStock.extra_set_total) === 0
          ? setStock.full_set_every_single
          : ((setStock.base_set_owned + setStock.extra_owned) / (setStock.base_set_total + setStock.extra_set_total)) * 100
      case 2: // base set only
        return setStock.full_set_base_only || setStock.base_set_total === 0
          ? setStock.full_set_base_only
          : (setStock.base_set_owned / setStock.base_set_total) * 100
      case 3: { // at least one version of every card
        const rarityTotal = current_set_commons.value + current_set_uncommons.value + current_set_rares.value + current_set_mythics.value
        return setStock.full_set_one_each || rarityTotal === 0
          ? setStock.full_set_one_each
          : ((setStock.commons + setStock.uncommons + setStock.rares + setStock.mythics) / rarityTotal) * 100
      }
      default:
        console.log("Something very wrong happened with page_options.full_set_option_selected on render")
        return 0
    }
  } else { return 0 }
})
const pageCount = computed(() => {
  const total_cards_to_display = current_set_base_cards.value.filter((card) => (card.name.toLowerCase().includes(card_search.value) || card_search.value == '')).length

  return (page_options && page_options.card_per_page_option_selected && (page_options.card_per_page_option_selected.value !== 4))
    ? Math.ceil(total_cards_to_display / page_options.card_per_page_option_selected.title) : 0
})
const pageSliceStart = computed(() => {
  return 0 + (page_options.card_per_page_option_selected.value !== 4
    ? (current_page.value - 1) * page_options.card_per_page_option_selected.title
    : 0)
})
const pageSliceEnd = computed(() => {
  return (page_options.card_per_page_option_selected.value !== 4
    ? Math.min(current_set_base_cards.value.length, current_page.value * page_options.card_per_page_option_selected.title)
    : current_set_base_cards.value.length)
})
const isMobile = computed(() => {
  return unref(display.mobile)
})
function on_scroll_stats_box() {
  stats_box_visible.value = window.scrollY > 280
}

// get progress for set by passing its code
function getProgressForSidebarSet(set_code) {
  if (collection_stock.o[set_code]) {
    switch (page_options.full_set_option_selected.value) {
      case 1: // every single card, variants included
        return collection_stock.o[set_code].full_set_every_single
      case 2: // base set only
        return collection_stock.o[set_code].full_set_base_only
      case 3: // at least one version of every card
        return collection_stock.o[set_code].full_set_one_each
      default:
        console.log("Something very wrong happened with page_options.full_set_option_selected on render")
        return 0
    }
  } else { return 0 }
}

function compareCards(a, b) {
  if (a.cardName < b.cardName) {
    return -1;
  }
  if (a.cardName > b.cardName) {
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

.auth_error {
  position: fixed;
  z-index: 10000;
  top: 12px;
  left: 12px;
  right: 12px;
}

.account_username {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 4px 0 8px;
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

.tech_logos {
  max-height: 60px;
  display: inline-block;
  margin-bottom: 10px;
}

.set_page_title {
  display: inline-block;
  font-weight: bold;
  font-size: 20pt;
  font-family: Georgia, 'Times New Roman', Times, serif;
  margin-left: 10px;
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
  cursor: pointer;
}

.set_list_element_selected_light {
  background-color: #FF899C;
  font-weight: bold;
}

.set_list_element_selected_dark {
  background-color: #9EC5F7;
  font-weight: bold;
}

.set_list_element_bar {
  position: relative;
  margin-top: -3px;
  width: 96%;
}

.set_logo,
.set_check {
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
  float: right;
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
  margin-top: -6px;
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

.card_finder_text_field {
  padding: 10px 20px;
}

.card_finder_results_list {
  height: 100%;
  max-height: 400px;
  overflow-y: auto;
}

.card_finder_results_element:hover {
  background-color: #F8BBD0;
}

.hover_card_image {
  position: fixed;
  width: 100%;
  max-width: 200px;
  z-index: 99999;
}

.v-card-item {
  /* used to avoid a weird overflow cutoff in the title of Export Collection */
  padding: 0.625rem 0;
}

.import_window {
  width: 100%;
  max-width: 500px;
  min-height: 330px;
  padding: 0 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
}

.import_status_message {
  max-width: min(90vw, 420px);
  margin-inline: auto;
  padding: 12px 20px;
  border-radius: 12px;
  background-color: rgb(var(--v-theme-surface));
  color: rgb(var(--v-theme-on-surface));
  box-shadow: 0 2px 8px rgb(0 0 0 / 20%);
}

.import_window_header {
  width: 100%;
  height: 70px;
}

.import_window_content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.import_syntax_selector :deep(.v-selection-control-group) {
  column-gap: 8px;
}

.import_text_field {
  width: 450px;
  max-width: 90%;
  height: 150px;
  align-self: center;
}

.import_file_field {
  width: 450px;
  max-width: 90%;
  height: 50px;
}

.import_action_options {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  align-self: stretch;
  width: 100%;
  margin-top: 6px;
  text-align: left;
}

.import_action_selector {
  grid-column: 1;
  grid-row: 1;
  min-width: 0;
}

.import_replace_confirmation {
  grid-column: 2;
  grid-row: 1;
  align-self: end;
  margin-bottom: 6px;
}

.import_password_field {
  grid-column: 1 / -1;
  grid-row: 2;
  width: 100%;
  margin-top: 8px;
}

.import_window_actions {
  margin-top: auto;
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

.housekeeping_window {
  width: 500px;
  height: 410px;
  text-align: center;
}

.housekeeping_window_header {
  width: 100%;
  height: 70px;
}

.housekeeping_window_body {
  padding: 0 20px;
}

.housekeeping_window_footer {
  padding: 0 20px;
}

.export_window {
  width: 100%;
  min-width: 350px;
  max-width: 500px;
  height: 200px;
  padding: 0 20px;
  text-align: center;
}

.about_window {
  width: 95%;
  max-width: 600px;
  height: 100%;
  text-align: center;
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
