var preprocessingCounter = 0
var modelCounter = 0

function addNewPreprocessing(){

  preprocessingCounterNext = preprocessingCounter + 1
  var preprocessingBlock = `
  <div id="preprocessing-element-to-replace-`+preprocessingCounter+`">
    <div class="container card-group my-3 px-0">
      <div class="card mx-0">
        <h4 class="card-header">{{ _("models.application_creation.select.preprocessing.stage.preprocessing") }} 1</h4>
        <div class="card-body">
          <select class="form-control" id="application_prepr_stages_ids" name="application_prepr_stages_ids">
            {% for method in data_prep_methods %}
              <option value="{{ method["id"] }}">{{ method["template_name"] }}</option>
            {% end %}
          </select>
        </div>
      </div>
      <div class="card mx-0">
        <h4 class="card-header">{{ _("models.application_creation.select.preprocessing.stage.config") }}</h4>
        <div class="card-body">
          <input class="text-input card-body w-100" id="application_prepr_stages_ids_0" name="application_prepr_stages_ids_config_0" />
        </div>
      </div>
    </div>
    <div>
      <button type="button" class="btn btn-primary" onclick="deleteCurrentPreprocessing('`+preprocessingCounter+`')">`+deletePreprocessingButtonText+`
    </div>
  </div>
  <div id="preprocessing-element-to-replace-`+preprocessingCounterNext+`"> </div>
  `
  var elementToReplace = document.getElementById("preprocessing-element-to-replace-"+preprocessingCounter).parentNode
  replace = '<div id="preprocessing-element-to-replace-'+preprocessingCounter+'"> </div>'

  elementToReplace.innerHTML = elementToReplace.innerHTML
  .replace(replace, preprocessingBlock)

  preprocessingCounter = preprocessingCounterNext
}

function deleteCurrentPreprocessing(preprocessingIndex){

  var elementToReplace = document.getElementById("preprocessing-element-to-replace-"+preprocessingIndex)
  elementToReplace.parentNode.removeChild(elementToReplace);

  // preprocessingCounter = preprocessingCounter - 1
}
