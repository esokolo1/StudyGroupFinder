let form_row_template = `
<div class="field is-horizontal">
  <div class="field-label">
    <label class="label has-text-weight-light"
      style="overflow-wrap:anywhere;" >
      {{label}}
    </label>
  </div>
  <div class="field-body">
    <slot></slot>
  </div>
</div>
`;
let form_row_component = {};
let init_form_row_component = (component) => {
  component.vue = Vue.extend({
    props:['label'],
    template:form_row_template,
  });
  Vue.component('form-row',component.vue);
};
init_form_row_component(form_row_component);
