(function () {
  function getById(id) {
    return id ? document.getElementById(id) : null;
  }

  function setOptions(selectEl, items, defaultLabel, includePincode) {
    if (!selectEl) return;
    var previousValue = selectEl.value;
    var html = '<option value="">' + defaultLabel + '</option>';
    var grouped = {};
    var groupOrder = [];

    items.forEach(function (item) {
      var districtName = item.district_name || '';
      if (!grouped[districtName]) {
        grouped[districtName] = [];
        groupOrder.push(districtName);
      }
      grouped[districtName].push(item);
    });

    groupOrder.forEach(function (districtName) {
      var groupItems = grouped[districtName];
      if (districtName) {
        html += '<optgroup label="' + districtName + '">';
      }
      groupItems.forEach(function (item) {
        var label = item.name;
        if (includePincode && item.pincode) {
          label += ' (' + item.pincode + ')';
        }
        html += '<option value="' + item.id + '">' + label + '</option>';
      });
      if (districtName) {
        html += '</optgroup>';
      }
    });

    selectEl.innerHTML = html;
    if (previousValue && items.some(function (i) { return String(i.id) === String(previousValue); })) {
      selectEl.value = previousValue;
    }
  }

  function fetchItems(url, onDone) {
    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function (response) { return response.ok ? response.json() : { items: [] }; })
      .then(function (data) { onDone((data && data.items) || []); })
      .catch(function () { onDone([]); });
  }

  function init(config) {
    var countrySelect = getById(config.countryId);
    var stateSelect = getById(config.stateId);
    var districtSelect = getById(config.districtId);
    var localitySelect = getById(config.localityId);
    var localitySearch = getById(config.localitySearchId);

    if (!countrySelect || !stateSelect || !districtSelect || !localitySelect) {
      return;
    }

    function loadStates() {
      var countryId = countrySelect.value;
      if (!countryId) {
        setOptions(stateSelect, [], 'All States');
        setOptions(districtSelect, [], 'All Districts');
        setOptions(localitySelect, [], 'All Localities');
        return;
      }
      fetchItems('/locations/api/states/?country_id=' + encodeURIComponent(countryId), function (items) {
        setOptions(stateSelect, items, 'All States');
        setOptions(districtSelect, [], 'All Districts');
        setOptions(localitySelect, [], 'All Localities');
      });
    }

    function loadDistricts() {
      var stateId = stateSelect.value;
      if (!stateId) {
        setOptions(districtSelect, [], 'All Districts');
        setOptions(localitySelect, [], 'All Localities');
        return;
      }
      fetchItems('/locations/api/districts/?state_id=' + encodeURIComponent(stateId), function (items) {
        setOptions(districtSelect, items, 'All Districts');
        setOptions(localitySelect, [], 'All Localities');
        loadLocalities();
      });
    }

    function loadLocalities() {
      var districtId = districtSelect.value;
      var stateId = stateSelect.value;
      var query = localitySearch ? localitySearch.value.trim() : '';
      if (!districtId && !stateId) {
        setOptions(localitySelect, [], 'All Localities');
        return;
      }
      var url = '/locations/api/localities/?';
      if (districtId) {
        url += 'district_id=' + encodeURIComponent(districtId);
      } else {
        url += 'state_id=' + encodeURIComponent(stateId);
      }
      if (query) {
        url += '&q=' + encodeURIComponent(query);
      }
      fetchItems(url, function (items) {
        setOptions(localitySelect, items, 'All Localities', true);
      });
    }

    countrySelect.addEventListener('change', loadStates);
    stateSelect.addEventListener('change', loadDistricts);
    districtSelect.addEventListener('change', loadLocalities);

    if (localitySearch) {
      var timeoutId = null;
      localitySearch.addEventListener('input', function () {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(loadLocalities, 250);
      });
    }
  }

  window.ZyroviaLocationDropdowns = { init: init };
})();
