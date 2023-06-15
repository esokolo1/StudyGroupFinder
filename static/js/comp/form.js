const form_row_tpl = `
<div class="field is-horizontal">
  <div class="field-label" v-if="label">
    <label class="label has-text-weight-light"
      style="overflow-wrap:anywhere;">
      {{label}}
    </label>
  </div>
  <div class="field-body">
    <div class="field"
      :class="{'is-narrow':narrow}">
      <div class="field"
        :class="{
          'is-grouped': group,
          'has-addons': joined,
          'is-grouped-right': right && !joined,
          'has-addons-right': right && joined,
        }">
        <slot></slot>
      </div>
      <p class="help" v-if="help">{{help}}</p>
      <p class="help is-danger" v-if="invalid">{{invalid}}</p>
    </div>
  </div>
</div>
`;
Vue.component('form-row', {
  props: {
    label: String,
    narrow: Boolean,
    group: Boolean,
    joined: Boolean,
    help: String,
    invalid: String,
    right: Boolean,
  },
  template: form_row_tpl,
});
/*------------------------------------------------------------*/
const ctrl_btn_tpl = `
<p class="control">
  <button class="button"
    :class="{'is-static':static}"
    @click="fxn ? fxn() : {}">
    <slot></slot>
  </button>
</p>
`;
Vue.component('ctrl-btn', {
  props: {
    fxn: Function,
    static: Boolean,
  },
  template: ctrl_btn_tpl,
});
