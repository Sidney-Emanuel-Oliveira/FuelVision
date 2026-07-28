package br.com.fuelvision.api.service;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import br.com.fuelvision.api.domain.CityLocation;
import br.com.fuelvision.api.domain.StateLocation;
import br.com.fuelvision.api.repository.LocationRepository;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class LocationServiceTest {

    @Mock
    private LocationRepository repository;

    @Test
    void returnsOnlyLocationsProvidedByTheRepository() {
        when(repository.findStatesWithPrices())
                .thenReturn(List.of(new StateLocation("RJ", "RIO DE JANEIRO")));
        LocationService service = new LocationService(repository);

        assertThat(service.findStates())
                .singleElement()
                .satisfies(state -> assertThat(state.code()).isEqualTo("RJ"));
    }

    @Test
    void normalizesStateBeforeLookingForCities() {
        when(repository.findCitiesWithPrices("RJ"))
                .thenReturn(List.of(new CityLocation(1L, "MACAE", "RJ")));
        LocationService service = new LocationService(repository);

        assertThat(service.findCities(" rj "))
                .singleElement()
                .satisfies(city -> assertThat(city.name()).isEqualTo("MACAE"));
        verify(repository).findCitiesWithPrices("RJ");
    }
}
