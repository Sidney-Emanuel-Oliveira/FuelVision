package br.com.fuelvision.api.service;

import br.com.fuelvision.api.dto.CityResponse;
import br.com.fuelvision.api.dto.StateResponse;
import br.com.fuelvision.api.repository.LocationRepository;
import java.util.List;
import java.util.Locale;
import org.springframework.stereotype.Service;

@Service
public class LocationService {

    private final LocationRepository repository;

    public LocationService(LocationRepository repository) {
        this.repository = repository;
    }

    public List<StateResponse> findStates() {
        return repository.findStatesWithPrices().stream()
                .map(state -> new StateResponse(state.code(), state.name()))
                .toList();
    }

    public List<CityResponse> findCities(String stateCode) {
        String normalizedState = stateCode.strip().toUpperCase(Locale.ROOT);
        return repository.findCitiesWithPrices(normalizedState).stream()
                .map(city -> new CityResponse(city.id(), city.name(), city.stateCode()))
                .toList();
    }
}
