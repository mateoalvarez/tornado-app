var preprocessingCounter = 1
var modelCounter = 1

function addNewPreprocessing(){

  preprocessingCounterNext = preprocessingCounter + 1
  var preprNameOptions = ``
  var i = 0
  for (i=0; i < preprocessingMethodNames.length; i++){
    preprNameOptions = preprNameOptions + '<option value=' + preprocessingMethodIds[i] + '>' + preprocessingMethodNames[i] + '</option>'
  }
  var preprocessingBlock = `
  <div id="preprocessing-element-to-replace-` + preprocessingCounter + `" class="w-100">
    <div class="container card-group my-3 px-0 w-100">
      <div class="card mx-0">
        <h4 class="card-header">` + modelsApplication_creationSelectPreprocessingStagePreprocessing + `</h4>
        <div class="card-body">
          <select class="form-control" id="application_prep_stages_ids" name="application_prep_stages_ids">
            ` + preprNameOptions + `
          </select>
        </div>
      </div>
      <div class="card mx-0">
        <h4 class="card-header">` + modelsApplication_creationSelectPreprocessingStageConfig + `</h4>
        <div class="card-body">
          <input class="text-input card-body w-100" id="application_prep_stages_ids_` + preprocessingCounterNext + `" name="application_prep_stages_ids_config" />
        </div>
      </div>
    </div>
    <div>
      <button type="button" class="btn btn-primary float-right" onclick="deleteCurrentPreprocessing('` + preprocessingCounter + `')">` + deletePreprocessingButtonText + `
    </div>
  </div>
  <div id="preprocessing-element-to-replace-` + preprocessingCounterNext + `"> </div>
  `
  var elementToReplace = document.getElementById("preprocessing-element-to-replace-"+preprocessingCounter).parentNode
  replace = '<div id="preprocessing-element-to-replace-'+preprocessingCounter+'"> </div>'

  elementToReplace.innerHTML = elementToReplace.innerHTML
  .replace(replace, preprocessingBlock)

  preprocessingCounter = preprocessingCounterNext
}

function deleteCurrentPreprocessing(preprocessingIndex){

  var elementToReplace = document.getElementById("preprocessing-element-to-replace-" + preprocessingIndex)
  elementToReplace.parentNode.removeChild(elementToReplace);

}

function addNewModel(){

  modelCounterNext = modelCounter + 1
  var modelNameOptions = ``
  var i = 0
  for (i=0; i < modelMethodNames.length; i++){
    modelNameOptions = modelNameOptions + '<option value=' + modelMethodIds[i] + '>' + modelMethodNames[i] + '</option>'
  }
  var modelBlock = `
  <div id="model-element-to-replace-` + modelCounter + `" class="w-100">
    <div class="container card-group my-3 px-0 w-100">
      <div class="card mx-0">
        <h4 class="card-header">` + modelsApplication_creationSelectModelStageModel + `</h4>
        <div class="card-body">
          <select class="form-control" id="application_models_ids" name="application_models_ids">
            ` + modelNameOptions + `
          </select>
        </div>
      </div>
      <div class="card mx-0">
        <h4 class="card-header">` + modelsApplication_creationSelectModelStageConfig + `</h4>
        <div class="card-body">
          <input class="text-input card-body w-100" id="application_prep_stages_ids_config_` + modelCounterNext + `" name="application_models_config" />
        </div>
      </div>
    </div>
    <div>
      <button type="button" class="btn btn-primary float-right" onclick="deleteCurrentModel('` + modelCounter + `')">` + deleteModelButtonText + `
    </div>
  </div>
  <div id="model-element-to-replace-` + modelCounterNext + `"> </div>
  `
  var elementToReplace = document.getElementById("model-element-to-replace-"+modelCounter).parentNode
  replace = '<div id="model-element-to-replace-'+modelCounter+'"> </div>'

  elementToReplace.innerHTML = elementToReplace.innerHTML
  .replace(replace, modelBlock)

  modelCounter = modelCounterNext
}

function deleteCurrentModel(modelIndex){

  var elementToReplace = document.getElementById("model-element-to-replace-" + modelIndex)
  elementToReplace.parentNode.removeChild(elementToReplace)

}
