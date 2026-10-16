import { injectable } from 'inversify';
import { FlaresolverrConfig } from '../types';
import { ProwlarrService } from './prowlarr-service';
import { EnvService } from './env-service';

@injectable()
export class FlaresolverrService {
  constructor(
    private envService: EnvService,
    private prowlarrService: ProwlarrService
  ) {
    this.config = {
      flaresolverrUrl: this.envService.get('FLARESOLVERR_URL') || 'http://byparr:8191',
      tagName: this.envService.get('FLARESOLVERR_TAG_NAME') || 'flaresolver'
    };
  }

  private config!: FlaresolverrConfig;

  async configureFlareSolverr(isDryRun: boolean = false): Promise<void> {
    const { flaresolverrUrl, tagName } = this.config;

    console.log('🔧 Configuring FlareSolverr as indexer proxy in Prowlarr...');

    if (isDryRun) {
      console.log('📋 Dry Run Mode - Would configure FlareSolverr proxy');
      return;
    }

    try {
      await this.ensureProwlarrReady();
      const tagId = await this.prowlarrService.ensureProxyTag(tagName);
      await this.prowlarrService.createOrUpdateProxy(flaresolverrUrl, tagId);

      console.log(`🏷️  Tag '${tagName}' (ID: ${tagId}) is assigned to FlareSolverr proxy.`);
      console.log('💡 Add this tag to indexers that need CloudFlare bypass.');

    } catch (error: any) {
      console.error('❌ Failed to configure FlareSolverr:', error.message);
      throw error;
    }
  }

  private async ensureProwlarrReady(): Promise<void> {
    console.log('🔍 Checking Prowlarr connectivity...');
    await this.prowlarrService.waitForService();
    console.log('✅ Prowlarr is ready!');
  }

}
